import 'bootstrap'
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-icons/font/bootstrap-icons.css'
import './assets/main.css'
import { createApp } from 'vue'
import Offline from './Offline.vue'

// TAFFISH local-only entry: no router, cloud API, job storage or authentication.
createApp(Offline).mount('#app')
