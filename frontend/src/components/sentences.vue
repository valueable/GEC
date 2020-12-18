<template>
  <div id="post" v-if="this.flag == 0">
    <el-row >


      <el-col :xs=22 :sm=22 :md=24 :lg=24 :xl=24>
  <el-row>
            <el-col  style="color: #F56C6C; white-space: pre-wrap" :xs=11 :sm=11 :md=12 :lg=12 :xl=12 >{{ item.orgsentence }}</el-col>
            <el-col  style="color: #67C23A; white-space: pre-wrap" :xs=11 :sm=11 :md=12 :lg=12 :xl=12>{{item.corrsentence}}</el-col>
          </el-row>
        <el-link v-for="tag in tags" type="danger" :key="tag.index" style="margin-right: 10px" :href="tag.itemHref">#{{tag.itemName}}</el-link>
        <el-row>

          <el-col :span=4>
            <el-button  icon="el-icon-delete" type="text" id='del' v-on:click="del">删除</el-button>
          </el-col>
        </el-row>
      </el-col>
    </el-row>
  </div>
</template>

<script>

/*
 * 该文件负责显示具体的某一条句子对
 * 其接收一个参数，为这条句子对的相关信息
 */

export default {
  name: 'sentences',
  props: ['item'],
  components: {},
  data: function () {
    return {
      tags: [],
      flag: 0,
    }
  },
  computed: {
    userLink: function () {
      return "/person/" + this.item.userID
    },
    avatarURL: function () {
      return "https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png"
    },
    isAdmin: function () {
      return true
    },
    curID: function () {
      return this.$route.params.id
    }
  },
  created: function () {
    var params = new URLSearchParams()
    params.append('senID', this.item.senID)

  },
  mounted: function () {
    this.getTagsList()
  },
  methods: {

    del: function () {
      this.$confirm('此操作将永久删除该动态, 是否继续?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        this.$http.get('/api/deleteSentences/?senId=' + this.item.senID)
                .then(res => {
                  this.flag = 1
                  this.$message({
                    type: "info",
                    message: "删除成功"
                  })
                })
      }).catch(() => {
        this.$message({
          type: 'info',
          message: '已取消删除'
        });
      });
    },
    getTagsList(){
          this.$http.get('/api/getTypeBySentence?senId='+this.item.senID)
              .then((response)=>{
                  var res1 = JSON.parse(response.bodyText)
                      if(res1['err_num']==0){
                          for(var i=0;i<res1['list'].length;i++){
                              this.tags.push({'itemName':res1['list'][i]['fields']['type'],
                                'itemHref':'/searchType/'+res1['list'][i]['fields']['type']})
                          }
                      }
              })
      },


  }
}
</script>

<style>
#post {
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  margin-bottom: 30px;
  padding: 10px;
  border-radius: 10px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  text-align: left;
}

.el-row {
  margin-bottom: 10px;
}
</style>
