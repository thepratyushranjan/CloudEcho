
function fixMongoDBPipeline(pipeline) {
  if (!Array.isArray(pipeline)) {
    return pipeline;
  }

  try {
    const pipelineStr = JSON.stringify(pipeline);
    
    // Check if fix is needed
    if (!pipelineStr.includes("'$") && !pipelineStr.includes("'_")) {
      return pipeline; // No fix needed
    }

    console.log("🔧 Fixing MongoDB pipeline - removing single quotes from keys");
    
    // Fix single quotes around keys
    const fixedStr = pipelineStr
      .replace(/"'(\$[^']+)'"\s*:/g, '"$1":')  // Fix "'$match'": -> "$match":
      .replace(/"'(_[^']+)'"\s*:/g, '"$1":')   // Fix "'_field'": -> "_field":
      .replace(/"'([a-zA-Z][^']+)'"\s*:/g, '"$1":');  // Fix "'field'": -> "field":
    
    const fixed = JSON.parse(fixedStr);
    console.log("✅ Pipeline fixed successfully");
    return fixed;
  } catch (err) {
    console.error("❌ Failed to fix pipeline:", err.message);
    return pipeline;
  }
}

/**
 * Wraps MCP tools to fix MongoDB pipeline issues
 * @param {Object} tools - Original MCP tools
 * @returns {Object} - Wrapped tools
 */
export function wrapTools(tools) {
  const wrapped = {};
  
  for (const [name, tool] of Object.entries(tools)) {
    if (name === 'mongo-http.aggregate') {
      // Wrap the aggregate tool to fix pipeline
      wrapped[name] = {
        ...tool,
        execute: async (params) => {
          console.log(`\n=== Intercepting ${name} ===`);
          console.log("Original params:", JSON.stringify(params, null, 2));
          
          // Fix the pipeline if it exists
          if (params.pipeline) {
            const fixed = fixMongoDBPipeline(params.pipeline);
            if (fixed !== params.pipeline) {
              console.log("Pipeline was fixed");
              params = { ...params, pipeline: fixed };
            }
          }
          
          console.log("Final params:", JSON.stringify(params, null, 2));
          
          // Call the original tool
          return tool.execute(params);
        }
      };
    } else {
      // Pass through other tools unchanged
      wrapped[name] = tool;
    }
  }
  
  return wrapped;
}
