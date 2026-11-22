import { createRouter, createWebHistory } from 'vue-router'
import HomeView from './views/HomeView.vue'
import AboutView from './views/AboutView.vue'
import NotFoundView from './views/NotFoundView.vue'

const routes = [
  { path: '/', component: HomeView, meta: { title: 'Welcome' } },
  { path: '/about', component: AboutView, meta: { title: 'About the library' } },
  { path: '/:rest(.*)*', component: NotFoundView, meta: { title: 'Page not found' } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: (to) => (to.hash ? { el: to.hash } : { top: 0 }),
})

router.afterEach((to) => {
  document.title = `${to.meta.title} | Northgate Library`
})

export default router
