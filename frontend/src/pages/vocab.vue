<template>
    <div id="analyze">
  <TopNav></TopNav>
<el-table :data="data" style="margin-left: 35%; margin-right: 35%">
  <el-table-column
    fixed
        prop="itemName"
        label="单词"
        width="180"
  style="alignment: center">
      </el-table-column>
      <el-table-column
        prop="itemCnt"
        label="使用次数"
        width="180">
      </el-table-column>
  <el-table-column
      label="操作"
      width="120">
      <template slot-scope="data">
        <el-button
          @click.native.prevent="deleteRow(data.$index, data.row)"
          type="primary">
          移除
          <i class="el-icon-delete el-icon--right"/>
        </el-button>
      </template>
    </el-table-column>
    </el-table>
    </div>
  <div v-if="data.length==0" style="margin-top: 20px">暂无搜索结果</div>
</template>

<script>
  import TopNav from "../components/topNav";
    export default {
        name: "vocab",
      components: {TopNav},
      mounted: function () {
    this.getCurUserID()
  },
  data: function () {
    return {
      userID: 0,
      data: []
    }
  },
  methods: {
    getCurUserID() {
        this.$http.get('/api/getCurUserID')
                .then((response) => {
                  var res1 = JSON.parse(response.bodyText)
                  if (res1['err_num'] == 0) {
                    this.userID = res1['userID'];
                    this.getVocab()
                  }
                })
      },
    getVocab(){
      this.$http.get('/api/getUserVocab?userId='+this.userID)
        .then((response)=>{
          var res1 = JSON.parse(response.bodyText)
                  if (res1['err_num'] == 0) {
                    for(var i=0;i<res1['list'].length;i++){
                              this.data.push({'itemName':res1['list'][i]['fields']['word'],
                                'itemCnt':res1['list'][i]['fields']['use_counts']})
                          }
                  }
        })
    },
    deleteRow(index, row){
      this.$http.get('/api/delWord?wordName='+row.itemName+'&userID='+this.userID)
        .then((response)=>{
          var res1 = JSON.parse(response.bodyText)
                  if (res1['err_num'] == 0) {
                    this.$message({type:'success',message:"删除成功",duration:600})
                    window.location.href="/vocab";
                  }
        })
    }

  }
    }
</script>

<style scoped>

</style>
