import { ToastProvider } from './components/toast/ToastProvider'
import { FolderBrowser } from './components/FolderBrowser'

function App() {
  return (
    <ToastProvider>
      <main>
        <h1>File System</h1>
        <FolderBrowser />
      </main>
    </ToastProvider>
  )
}

export default App
