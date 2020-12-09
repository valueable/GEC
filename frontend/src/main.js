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
Vue.prototype.$echarts = echarts;
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
      path: '/index',
      name: 'index',
      component: index
    },

  ],
  mode: 'history'
})
new Vue({
  render: h => h(App),
  router,
}).$mount('#app')
