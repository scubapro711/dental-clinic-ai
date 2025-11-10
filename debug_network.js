/**
 * Network Debugging Script
 * Inject this into browser console to capture detailed network information
 */

(function() {
  console.log('🔍 Network Debugger Started');
  console.log('==========================');
  
  // Store original XMLHttpRequest and fetch
  const originalXHR = window.XMLHttpRequest;
  const originalFetch = window.fetch;
  
  // Create a log array
  window.__networkLog = [];
  
  // Intercept XMLHttpRequest
  window.XMLHttpRequest = function() {
    const xhr = new originalXHR();
    const originalOpen = xhr.open;
    const originalSend = xhr.send;
    
    let requestData = {
      type: 'XMLHttpRequest',
      method: null,
      url: null,
      headers: {},
      body: null,
      timestamp: null,
      response: null,
      status: null,
      error: null
    };
    
    xhr.open = function(method, url, ...args) {
      requestData.method = method;
      requestData.url = url;
      requestData.timestamp = new Date().toISOString();
      console.log(`📤 XHR ${method} ${url}`);
      return originalOpen.apply(this, [method, url, ...args]);
    };
    
    xhr.send = function(body) {
      requestData.body = body;
      
      xhr.addEventListener('load', function() {
        requestData.status = xhr.status;
        requestData.response = xhr.responseText;
        console.log(`✅ XHR Response ${requestData.status} from ${requestData.url}`);
        window.__networkLog.push({...requestData});
      });
      
      xhr.addEventListener('error', function() {
        requestData.error = 'Network Error';
        console.error(`❌ XHR Error for ${requestData.url}`);
        console.error('Error details:', {
          readyState: xhr.readyState,
          status: xhr.status,
          statusText: xhr.statusText
        });
        window.__networkLog.push({...requestData});
      });
      
      xhr.addEventListener('abort', function() {
        requestData.error = 'Request Aborted';
        console.warn(`⚠️  XHR Aborted for ${requestData.url}`);
        window.__networkLog.push({...requestData});
      });
      
      return originalSend.apply(this, arguments);
    };
    
    return xhr;
  };
  
  // Intercept fetch
  window.fetch = function(url, options = {}) {
    const requestData = {
      type: 'fetch',
      method: options.method || 'GET',
      url: url,
      headers: options.headers || {},
      body: options.body || null,
      timestamp: new Date().toISOString(),
      response: null,
      status: null,
      error: null
    };
    
    console.log(`📤 FETCH ${requestData.method} ${url}`);
    console.log('   Headers:', options.headers);
    console.log('   Body:', options.body);
    
    return originalFetch.apply(this, arguments)
      .then(response => {
        requestData.status = response.status;
        console.log(`✅ FETCH Response ${response.status} from ${url}`);
        window.__networkLog.push({...requestData});
        return response;
      })
      .catch(error => {
        requestData.error = error.message;
        console.error(`❌ FETCH Error for ${url}`);
        console.error('Error:', error);
        console.error('Error name:', error.name);
        console.error('Error message:', error.message);
        console.error('Error stack:', error.stack);
        window.__networkLog.push({...requestData});
        throw error;
      });
  };
  
  // Helper function to export logs
  window.exportNetworkLog = function() {
    console.log('📊 Network Log Export');
    console.log('====================');
    console.log(JSON.stringify(window.__networkLog, null, 2));
    return window.__networkLog;
  };
  
  console.log('✅ Network Debugger Ready');
  console.log('   - All XHR and fetch requests will be logged');
  console.log('   - Use window.exportNetworkLog() to see all captured requests');
  console.log('');
})();
