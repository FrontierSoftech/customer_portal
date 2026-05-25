import vue from "@vitejs/plugin-vue";
import frappeui from "frappe-ui/vite";
import path from "path";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [
    frappeui({
      frappeProxy: true,
      lucideIcons: true,
      jinjaBootData: true,
      buildConfig: {
        outDir: "../customer_portal/public/portal",
        emptyOutDir: true,
        indexHtmlPath: "../customer_portal/www/portal/index.html",
      },
    }),
    vue(),
  ],
  resolve: {
    alias: { "@": path.resolve(__dirname, "src") },
  },
  server: { allowedHosts: true, fs: { allow: [".."] } },
});
