// Content script initialization
console.log('VocalLens-AI Content Script Loaded');

// Handle messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log('Message received in content:', request);
  
  // Add message handling logic
  switch(request.type) {
    case 'POPUP_MOUNTED':
      sendResponse({ status: 'connected' });
      break;
    default:
      console.log('Unknown message type:', request.type);
  }
  
  return true; // Will respond asynchronously
});