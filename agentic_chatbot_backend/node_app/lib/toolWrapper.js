/**
 * Fixes single-quote issue in MongoDB pipelines
 * Converts {"'$match'": ...} to {"$match": ...}
 */
export function fixMongoDBPipeline(pipeline) {
  if (!Array.isArray(pipeline)) {
    return pipeline;
  }

  try {
    const pipelineStr = JSON.stringify(pipeline);
    
    // Check if fix is needed
    if (!pipelineStr.includes("'$") && !pipelineStr.includes("'_")) {
      return pipeline;
    }
    
    // Fix single quotes around keys
    const fixedStr = pipelineStr
      .replace(/"'(\$[^']+)'"\s*:/g, '"$1":')
      .replace(/"'(_[^']+)'"\s*:/g, '"$1":')
      .replace(/"'([a-zA-Z][^']+)'"\s*:/g, '"$1":');
    
    return JSON.parse(fixedStr);
  } catch (err) {
    console.error("Failed to fix pipeline:", err.message);
    return pipeline;
  }
}

/**
 * Wraps MCP tools to fix MongoDB pipeline issues before execution
 * @param {Object} tools - Original MCP tools
 * @returns {Object} - Wrapped tools with pipeline fixes
 */
export function wrapMongoTools(tools) {
  const wrapped = {};
  
  for (const [name, tool] of Object.entries(tools)) {
    if (name === 'mongo-http.aggregate') {
      wrapped[name] = {
        description: tool.description,
        parameters: tool.parameters,
        execute: async (params) => {
          if (params.pipeline) {
            // Parse pipeline if it's a string
            let pipeline = params.pipeline;
            if (typeof pipeline === 'string') {
              try {
                pipeline = JSON.parse(pipeline);
              } catch (err) {
                console.error("Failed to parse pipeline:", err.message);
              }
            }
            
            // Fix single-quote issues
            const fixedPipeline = fixMongoDBPipeline(pipeline);
            params = { ...params, pipeline: fixedPipeline };
          }

          return tool.execute(params);
        }
      };
    } else {
      wrapped[name] = tool;
    }
  }
  
  return wrapped;
}
