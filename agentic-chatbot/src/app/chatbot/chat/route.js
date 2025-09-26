import { NextResponse } from "next/server";
import { loadAllMCPTools } from "@/app/lib/mcp.js";
import { looksDbRelated, buildToolSet, loadDomainInstruction } from "@/app/lib/agent.js";
import {
  validateRequest,
  formatResponse,
  extractBetween,
  createStreamResponse,
  requiresTools
} from "../../utils/chatUtils.js";
import {
  processWithTools,
  processWithoutTools
} from "../../handlers/chatHandlers.js";

export const runtime = "nodejs";

// CORS configuration - Allow all origins
const CORS_CONFIG = {
  origin: '*',
  methods: 'GET, POST, PUT, DELETE, OPTIONS, PATCH',
  headers: 'Content-Type, Authorization, X-Requested-With, Accept, Origin',
};

// Create CORS headers
const createCorsHeaders = () => ({
  'Access-Control-Allow-Origin': CORS_CONFIG.origin,
  'Access-Control-Allow-Methods': CORS_CONFIG.methods,
  'Access-Control-Allow-Headers': CORS_CONFIG.headers,
  'Access-Control-Allow-Credentials': 'true',
  'Access-Control-Max-Age': '86400', // Cache preflight for 24 hours
});

// Error response factory
const createErrorResponse = (message, status = 500) => {
  return NextResponse.json(
    { error: message },
    { status, headers: createCorsHeaders() }
  );
};

// Success response factory
const createSuccessResponse = (data) => {
  return NextResponse.json(data, { headers: createCorsHeaders() });
};

// Extract and format response content
const extractResponseContent = (formattedText) => {
  const reasoning = extractBetween(formattedText, "<EXPLANATION>", "</EXPLANATION>");
  const content = extractBetween(formattedText, "<CONTENT>", "</CONTENT>") || formattedText;
  return { reasoning, content };
};

// Process the chat request
const processChatRequest = async (query, history, streamMode) => {
  const { tools: allTools, closeAll } = await loadAllMCPTools();
  
  try {
    const safeTools = buildToolSet(allTools, query);
    const domain = loadDomainInstruction();
    const needsTools = requiresTools(query, safeTools) || looksDbRelated(query);
    const hasTools = Object.keys(safeTools).length > 0;
    
    // Select processing strategy
    const processStrategy = needsTools && hasTools ? processWithTools : processWithoutTools;
    const processorArgs = needsTools && hasTools 
      ? [query, history, safeTools, domain]
      : [query, history, domain];
    
    const { result, finalText, toolsExecuted, plannedToolNames } = 
      await processStrategy(...processorArgs);
    
    const formattedText = formatResponse(finalText, toolsExecuted);
    const { reasoning, content } = extractResponseContent(formattedText);
    
    // Build response data
    const responseData = {
      content,
      reasoning,
      plannedToolNames,
      result,
      toolsExecuted,
      modelUsed: needsTools ? "gemini-2.5-pro" : "gemini-2.5-flash",
    };
    
    // Handle streaming response
    if (streamMode) {
      const streamResponse = await createStreamResponse(
        content,
        reasoning,
        plannedToolNames,
        result,
        toolsExecuted
      );
      
      // Apply CORS headers to stream response
      Object.entries(createCorsHeaders()).forEach(([key, value]) => {
        streamResponse.headers.set(key, value);
      });
      
      return streamResponse;
    }
    
    // Return standard JSON response
    return createSuccessResponse({
      result: content,
      reasoning,
      plannedTools: plannedToolNames,
      toolCalls: result?.toolCalls || [],
      toolResults: result?.toolResults || [],
      toolsExecuted,
      modelUsed: responseData.modelUsed,
    });
    
  } finally {
    // Ensure resources are cleaned up
    if (closeAll) {
      try {
        await closeAll();
      } catch {
        // Silently handle cleanup errors
      }
    }
  }
};

// OPTIONS Request for CORS preflight
export async function OPTIONS() {
  return new Response(null, { headers: createCorsHeaders() });
}

// POST Request - Main chat endpoint
export async function POST(req) {
  try {
    // Parse request parameters
    const url = new URL(req.url);
    const streamMode = url.searchParams.get("stream") === "1";
    const body = await req.json();
    const { query, history } = validateRequest(body);
    
    // Process the chat request
    return await processChatRequest(query, history, streamMode);
    
  } catch (err) {
    // Handle different error types
    const errorMessage = err?.name === "AbortError"
      ? "Timed out waiting for model/tools"
      : err?.message || "Internal Error";
    
    return createErrorResponse(errorMessage);
  }
}