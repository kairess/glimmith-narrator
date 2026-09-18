const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('glimmith', {
  onPlayLine: (callback) => {
    ipcRenderer.on('play-line', (_event, payload) => callback(payload));
  },
  notifyFinished: () => ipcRenderer.send('line-finished'),
});
