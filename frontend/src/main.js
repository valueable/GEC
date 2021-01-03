// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import App from './App.vue'
import './plugins/element.js'
import VueRouter from 'vue-router'
import axios from 'axios'
import { InfiniteScroll } from 'element-ui'
import VueResource from 'vue-resource'
import echarts from 'echarts'

import index from './pages/index'
import login from './pages/login'
import register from './pages/register'
import home from './pages/home'
import searchType from './pages/searchType'
import analyze from './pages/analyze'
import edituser from './pages/edituser'
import vocab from './pages/vocab'
import corrfiles from './pages/corrfiles'


Vue.config.productionTip = false;
Vue.use(VueRouter);
Vue.use(VueResource);
Vue.use(InfiniteScroll);

Vue.prototype.$axios = axios;
axios.defaults.headers.post['Content-Type'] = 'application/json';

/* eslint-disable no-new */
const router = new VueRouter({
  routes: [
    {
      path: '/',
      name: 'init',
      component: index
    },
    {
      path: '/index',
      name: 'index',
      component: index
    },
    {
      path: '/login',
      name: 'login',
      component: login
    },
    {
      path: '/register',
      name: 'register',
      component: register
    },
    {
      path: '/home',
      name: 'home',
      component: home
    },
    {
      path: '/searchType/:key',
      name: 'searchType',
      component: searchType
    },
    {
      path: '/analyze',
      name: 'analyze',
      component: analyze
    },
    {
      path: '/edituser',
      name: 'edituser',
      component: edituser
    },
    {
      path: '/vocab',
      name: 'vocab',
      component: vocab
    },
    {
      path: '/corrfiles',
      name: 'corrfiles',
      component:corrfiles
    },

  ],
  mode: 'history'
});
new Vue({
  render: h => h(App),
  router,
}).$mount('#app')
