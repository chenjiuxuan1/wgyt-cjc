import { defineConfig } from "vite"
import vue from "@vitejs/plugin-vue"
import path from "path"

function resolve(url) {
  return path.resolve(__dirname, url)
}
// https://vitejs.dev/config/
export default defineConfig({
  base: "",  // 修改为空字符串
  assetsInclude: ["**/*.glb", "**/*.gltf", "**/*.fbx", "**/*.hdr", "**/*.json", "**/*.mp4", "**/*.mov"],
  server: {
    port: 5173,
    host: true,
    cors: true,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5173',
        changeOrigin: true,
        secure: false
      }
    },
    hmr: {
      clientPort: 4443,  // 修改为Ngrok的端口
      host: 'wgyt.free.idcfengye.com'  // 修改为你的Ngrok域名
    }
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, 'src'),
      "~@": resolve("./src"),
    },
    extensions: [".mjs", ".js", ".jsx", ".json", ".vue"],
  },
  plugins: [vue()],
  build: {
    chunkSizeWarningLimit: 1500,
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('node_modules')) {
            return 'vendor'
          }
        }
      }
    }
  }
})
