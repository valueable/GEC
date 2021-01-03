<template>
    <div id="corrfiles">
  <TopNav></TopNav>
<el-table :data="data" style="margin-left: 35%; margin-right: 35%;" border="true">
  <el-table-column
    fixed
        prop="itemName"
        label="上传文件名"
        width="180"
  style="alignment: center">
      </el-table-column>
      <el-table-column
        prop="itemCnt"
        label="改错个数"
        width="180">
      </el-table-column>
<el-table-column
      label="下载修改后的文件"
      width="150">
      <template slot-scope="data">
        <a :href="download(data.$index, data.row)">下载文件</a>
      </template>
    </el-table-column>
  <el-table-column
      label="操作"
      width="150">
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
      <div v-if="data.length==0" style="margin-top: 20px">暂无搜索结果</div>
    </div>
</template>

<script>
  import TopNav from "../components/topNav";
    export default {
        name: "corrfiles",
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
                    this.getFiles()
                  }
                })
      },
    getFiles(){
      this.$http.get('/api/showFiles?userId='+this.userID)
        .then((response)=>{
          var res1 = JSON.parse(response.bodyText)
                  if (res1['err_num'] == 0) {
                    for(var i=0;i<res1['list'].length;i++){
                              this.data.push({'itemName':res1['list'][i]['fields']['org_doc'],
                                'time':res1['list'][i]['fields']['dateTime'],
                                'corrname':res1['list'][i]['fields']['res_doc_name'],
                                'itemCnt':res1['list'][i]['fields']['error_cnt']})
                          }
                  }
        })
    },
    deleteRow(index, row){
      this.$http.get('/api/deleteFile?filename='+row.itemName+'&userID='+this.userID+'&res_doc='+row.corrname)
        .then((response)=>{
          var res1 = JSON.parse(response.bodyText)
                  if (res1['err_num'] == 0) {
                    this.$message({type:'success',message:"删除成功",duration:600})
                    window.location.href="/corrfiles";
                  }
        })
    },
download(index, row){
        return '/api/downloadFile?userId='+this.userID+'&filename='+row.corrname
    },
  }

    }
</script>

<style scoped>

</style>
