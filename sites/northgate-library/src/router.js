import { createRouter, createWebHistory } from 'vue-router'
import HomeView from './views/HomeView.vue'
import AboutView from './views/AboutView.vue'
import SearchView from './views/SearchView.vue'
import BookView from './views/BookView.vue'
import ReserveView from './views/ReserveView.vue'
import ReservedView from './views/ReservedView.vue'
import HoursView from './views/HoursView.vue'
import NotFoundView from './views/NotFoundView.vue'

const routes = [
  { path: '/', component: HomeView, meta: { title: 'Welcome' } },
  { path: '/search', component: SearchView, meta: { title: 'Search the catalogue' } },
  { path: '/book/:id', component: BookView },
  { path: '/reserve/:id', component: ReserveView },
  { path: '/reserved', component: ReservedView, meta: { title: 'Reservation confirmed' } },
  { path: '/hours', component: HoursView, meta: { title: 'Opening hours' } },
  { path: '/about', component: AboutView, meta: { title: 'About the library' } },
  { path: '/:rest(.*)*', component: NotFoundView, meta: { title: 'Page not found' } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: (to) => (to.hash ? { el: to.hash } : { top: 0 }),
})

router.afterEach((to) => {
  // Pages without a fixed title set their own.
  if (to.meta.title) document.title = `${to.meta.title} | Northgate Library`
})

export default router
