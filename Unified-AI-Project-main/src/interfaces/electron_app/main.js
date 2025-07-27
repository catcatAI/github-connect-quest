const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');

let pythonExecutable = 'python';

function loadPythonPath() {
    const envPath = path.join(__dirname, '..', '..', '..', '.env');
    if (fs.existsSync(envPath)) {
        const envFileContent = fs.readFileSync(envPath, 'utf8');
        const match = envFileContent.match(/^PYTHON_EXECUTABLE=(.*)$/m);
        if (match && match[1]) {
            pythonExecutable = match[1].trim();
            console.log(`Main Process: Found Python executable path: ${pythonExecutable}`);
        } else {
            console.log("Main Process: .env file found, but PYTHON_EXECUTABLE not set. Using default 'python'.");
        }
    } else {
        console.log("Main Process: .env file not found. Using default 'python'.");
    }
}

function createWindow () {
  const mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false
    }
  });

  mainWindow.loadFile(path.join(__dirname, 'index.html'));
  // mainWindow.webContents.openDevTools();
}

app.whenReady().then(() => {
  loadPythonPath();
  createWindow();

  app.on('activate', function () {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', function () {
  if (process.platform !== 'darwin') app.quit();
});

ipcMain.handle('game:start', async () => {
  console.log("Main Process: Received 'game:start' request from renderer.");
  const gameProcess = spawn(pythonExecutable, [path.join(__dirname, '..', '..', 'game', 'main.py')]);

  gameProcess.stdout.on('data', (data) => {
    console.log(`Game stdout: ${data}`);
  });

  gameProcess.stderr.on('data', (data) => {
    console.error(`Game stderr: ${data}`);
  });

  gameProcess.on('close', (code) => {
    console.log(`Game process exited with code ${code}`);
  });
});
