import { createApp } from 'vue'
import '@fontsource/literata/600.css'
import '@fontsource/literata/700.css'
import '@fontsource/source-sans-3/400.css'
import '@fontsource/source-sans-3/600.css'
import '@fontsource/source-sans-3/700.css'
import './styles.css'
import App from './App.vue'
import router from './router.js'

createApp(App).use(router).mount('#app')
