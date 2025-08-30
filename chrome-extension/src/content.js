console.log('MKD Automation content script loaded');

let isRecording = false;
let recordedActions = [];

function recordAction(type, data) {
  if (isRecording) {
    recordedActions.push({
      type,
      data,
      timestamp: Date.now(),
      url: window.location.href
    });
  }
}

document.addEventListener('click', (e) => {
  recordAction('click', {
    x: e.clientX,
    y: e.clientY,
    target: e.target.tagName,
    id: e.target.id,
    className: e.target.className
  });
});

document.addEventListener('input', (e) => {
  recordAction('input', {
    target: e.target.tagName,
    id: e.target.id,
    className: e.target.className,
    value: e.target.value
  });
});

document.addEventListener('keydown', (e) => {
  if (e.ctrlKey || e.metaKey || e.altKey) {
    recordAction('keydown', {
      key: e.key,
      code: e.code,
      ctrlKey: e.ctrlKey,
      metaKey: e.metaKey,
      altKey: e.altKey,
      shiftKey: e.shiftKey
    });
  }
});

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'startRecording') {
    isRecording = true;
    recordedActions = [];
    sendResponse({ success: true });
  } else if (request.action === 'stopRecording') {
    isRecording = false;
    sendResponse({ actions: recordedActions });
    recordedActions = [];
  } else if (request.action === 'getStatus') {
    sendResponse({ isRecording });
  }
  return true;
});