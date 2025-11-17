/**
 * Validates and fixes a MongoDB aggregation pipeline
 * @param {Array} pipeline - The pipeline array to validate
 * @returns {Object} - {isValid: boolean, fixed: Array, errors: Array}
 */
export function validateAndFixPipeline(pipeline) {
  const errors = [];
  
  if (!Array.isArray(pipeline)) {
    return {
      isValid: false,
      fixed: pipeline,
      errors: ['Pipeline must be an array']
    };
  }

  try {
    // Convert to JSON and back to ensure proper serialization
    const jsonStr = JSON.stringify(pipeline);
    
    // Check for double-quoted stage operators (the main issue)
    const doubleQuotePattern = /["']\\?"?\$match\\?"?["']/g;
    if (doubleQuotePattern.test(jsonStr)) {
      errors.push('Detected double-quoted stage operators');
    }
    
    // Check for ISODate usage (should be plain strings)
    if (jsonStr.includes('ISODate')) {
      errors.push('Detected ISODate() usage - dates should be plain ISO strings');
    }
    
    // Check for {"$date": ...} format (should be plain strings)
    if (jsonStr.includes('"$date"')) {
      errors.push('Detected {"$date": ...} format - dates should be plain ISO strings');
    }
    
    const fixed = JSON.parse(jsonStr);
    
    return {
      isValid: errors.length === 0,
      fixed,
      errors
    };
  } catch (err) {
    return {
      isValid: false,
      fixed: pipeline,
      errors: [`JSON serialization error: ${err.message}`]
    };
  }
}

/**
 * Logs pipeline validation results
 * @param {string} toolName - Name of the tool being called
 * @param {Object} validation - Validation result
 */
export function logPipelineValidation(toolName, validation) {
  if (!validation.isValid) {
    console.warn(`\n⚠️  Pipeline Validation Warning for ${toolName}:`);
    validation.errors.forEach(err => console.warn(`   - ${err}`));
    console.warn('   Pipeline:', JSON.stringify(validation.fixed, null, 2));
  } else {
    console.log(`✅ Pipeline validation passed for ${toolName}`);
  }
}

/**
 * Validates tool input before execution
 * @param {Object} toolCall - The tool call object
 * @returns {Object} - Validated/fixed tool call
 */
export function validateToolInput(toolCall) {
  if (toolCall.toolName === 'mongo-http.aggregate' && toolCall.input?.pipeline) {
    const validation = validateAndFixPipeline(toolCall.input.pipeline);
    logPipelineValidation(toolCall.toolName, validation);
    
    if (!validation.isValid) {
      console.warn('⚠️  Proceeding with potentially malformed pipeline');
    }
    
    return {
      ...toolCall,
      input: {
        ...toolCall.input,
        pipeline: validation.fixed
      }
    };
  }
  
  return toolCall;
}
