// Initialize extension
chrome.runtime.onInstalled.addListener(() => {
  console.log('VocalLens-AI Extension installed');
});

// Handle messages
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log('Message received in background:', request);
  
  // Add specific message handling logic here
  switch(request.type) {
    case 'START_RECORDING':
      // Handle start recording
      break;
    case 'STOP_RECORDING':
      // Handle stop recording
      break;
    default:
      console.log('Unknown message type:', request.type);
  }
  
  return true; // Will respond asynchronously
});