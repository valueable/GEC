<template>
  <div id="person">
    <!-- TODO: 该menu不需要在此实现，需要使用component中的topNav.vue替换 -->
    <TopNav/>

    <el-container heigth = "100%">
      <el-container>
        <el-aside>
          <span v-infinite-scroll="load" :infinite-scroll-disabled="busy" :infinite-scroll-distance="10">
<list v-bind:title="title1" v-bind:itemList="tagData"/>

          </span>
        </el-aside>

        <el-main>
          <span v-infinite-scroll="loadMore" :infinite-scroll-disabled="busy" :infinite-scroll-distance="10">
            <sentences v-for="item in data" :item = "item" :key = "item.index"/>
          </span>
          <div v-if="isPostEmpty==1" style="margin-top: 20px">暂无搜索结果</div>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script>

import { infiniteScroll } from 'vue-infinite-scroll'
import sentences from '../components/sentences'
import TopNav from '../components/topNav'
import list from '../components/list'

export default {
  name: 'home',
  directives: {
    infiniteScroll
  },
  components: {
    TopNav,
    sentences,
    list
  },
  mounted: function () {
    this.getCurUserID()
  },
  data: function () {
    return {
      userID: 0,
      busy: false,
      count: 0,
      data: [],
      tagData: [],
      title1: '常错类型',
      isPostEmpty: 0
    }
  },
  methods: {
    getCurUserID() {
        this.$http.get('/api/getCurUserID')
                .then((response) => {
                  var res1 = JSON.parse(response.bodyText)
                  if (res1['err_num'] == 0) {
                    this.userID = res1['userID'];
                    this.getTagsList()
                    this.getSentences()
                  }
                })
      },
    getTagsList() {
      this.$http.get('/api/getOftenTypes?userId='+this.userID)
        .then((response) => {
          var res1 = JSON.parse(response.bodyText)
          if (res1['err_num'] == 0) {

            for (var i = 0; i < res1['list'].length; i++) {
              this.tagData.push({
                'itemName': res1['list'][i]['fields']['type'],
                'itemHref': '/searchType/' + res1['list'][i]['fields']['type']
              })
            }
          }
        })
    },
    getSentences() {
      this.$http.get('/api/getUserSentences?userId='+this.userID)
        .then((response) => {
          var res1 = JSON.parse(response.bodyText)
          if (res1['err_num'] == 0) {
            for (var i = 0; i < res1['list'].length; i++) {
              var str = res1['list'][i]['fields']['org_sen']
              var str2 = res1['list'][i]['fields']['corr_sen']
              this.data.push({
                'senID': res1['list'][i]['pk'],
                'orgsentence': str,
                'corrsentence': str2,

              })
            }
          }
          if (this.data.length == 0) {
            this.isPostEmpty = 1
          }
        })
    }
  }
}
</script>

<style>
  .el-header {
    background: #FFF;
    color: #333;
    font-size: 30px;
  }

  .el-aside {
    padding: 10px;
  }

  .el-main {
    padding: 10px
  }
</style>
