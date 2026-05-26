import path from 'path';
import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import Icons from 'unplugin-icons/vite';
import proxyOptions from './proxyOptions';

// https://vitejs.dev/config/
export default defineConfig({
	plugins: [
		vue(),
		Icons({ compiler: 'vue3', autoInstall: false }),
	],
	server: {
		port: 8080,
		host: '0.0.0.0',
		proxy: proxyOptions
	},
	resolve: {
		alias: {
			'@': path.resolve(__dirname, 'src')
		}
	},
	build: {
		outDir: '../customer_portal/public/dashboard',
		emptyOutDir: true,
		target: 'es2015',
	},
});
