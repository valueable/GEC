<template>
  <div id="searchtag">

  <top />
<el-container heigth = "100%">

          <el-header style="text-align: center;color: black;font-size: x-large" >
              <h style="text-align: center">Tag：{{searchContent}}</h>
          </el-header>
 <el-container >

<el-main>
<h style="font-size: large">相关句子集</h>
     <br/>
        <span v-if="isPostEmpty==0" v-infinite-scroll="load" :infinite-scroll-disabled="busy" :insenfinite-scroll-distance="10">
            <post  v-for="item in this.senData" :item = "item" :key = "item.index"/>
          </span>
            <div v-if="isPostEmpty==1" style="margin-top: 20px">暂无搜索结果</div>
</el-main>


         </el-container >
      </el-container>

  </div>
</template>

<script>
import post from '../components/sentences'

import top from '../components/topNav'
export default {
  name: 'searchType',
  components: {
    top,
    post
  },
  mounted:function(){
    this.getUserID()

  },
  data: function () {
    return {
      input:"",
      title1:'相关用户',
      senData:[],
      count:0,
      userID: 0,
        isPostEmpty:0
    }
  },
    computed: {
        searchContent: function () {
            return this.$route.params.key
        },
    },
  methods: {
    load () {
        if(this.count<10){
            this.count++
        }
      },
    getUserID(){
      this.$http.get('/api/getCurUserID')
                .then((response) => {
                  var res1 = JSON.parse(response.bodyText)
                  if (res1['err_num'] == 0) {
                    this.userID = res1['userID'];
                    this.searchSen()
                  }
                })
    },
         searchSen(){
          this.$http.get('/api/getSentenceByType?userId='+this.userID+'&typeName='+this.$route.params.key)
              .then((response)=>{
                  var res1 = JSON.parse(response.bodyText)
                      if(res1['err_num']==0){
                          for(var i=0;i<res1['list'].length;i++){
                              var str = res1['list'][i]['fields']['org_sen']
              var str2 = res1['list'][i]['fields']['corr_sen']
              this.senData.push({
                'senID': res1['list'][i]['pk'],
                'orgsentence': str,
                'corrsentence': str2,

              })
                          }
                          if(this.senData.length==0){
                              this.isPostEmpty=1
                          }
                      }
                      else{
                        this.$message.error("暂无结果")
                      }
              })
      }

    }
}
</script>




