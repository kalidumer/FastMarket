import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';
// https://vite.dev/config/
export default defineConfig({
    plugins: [react()],
    resolve: {
        alias: {
            // Maps the '@' shortcut directly and cleanly to your 'src' folder
            '@': path.resolve(new URL('.', import.meta.url).pathname, './src'),
        },
    },
});
