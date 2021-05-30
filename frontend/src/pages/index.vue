<template>
 <div id="index">
   <top />
<el-container heigth = "100%" >

          <el-header style="text-align: center;font-size: x-large; margin-top: 30px; background: white" >
              <h style="text-align: center">语法纠错</h>
          </el-header>
 <el-container >
<el-main>
<el-container>
  <el-input
  type="textarea"
  placeholder="请输入内容"
  v-model="error_sentence"
  maxlength="500"
  show-word-limit
  :rows="10"
  style="font-size: 20px;color: #3a8ee6"
> </el-input>
    <el-input
  type="textarea"
  placeholder="改错结果"
  v-model="correct_sentence"
  :rows="10"
  disabled="true"
style="font-size: 20px;color: #3a8ee6; "
>
</el-input>
</el-container>
  <el-container>
    <el-upload v-if="this.userId > 0"
  class="upload-demo"
  ref="upload"
  accept=".txt"
  action="/api/upLoad/"
  :on-preview="handlePreview"
  :on-remove="handleRemove"
  :limit = 1
  :data={userId:this.userId}
  :file-list="fileList"
  :name = 'file'
  :on-success = "handleSuccess"
  :auto-upload="false">
  <el-button slot="trigger" size="small" type="primary">选取文件<i class="el-icon-folder"/> </el-button>
  <el-button style="margin-left: 10px;" size="small" type="success" @click="submitUpload">上传<i class="el-icon-upload"/> </el-button>
  <div slot="tip" class="el-upload__tip">只能上传txt文件，且不超过500kb</div>
</el-upload>
    <el-button type="primary" style="margin-left: 30%" @click="correct">改错<i class="el-icon-check el-icon--right"></i></el-button>
    <el-button type="primary"  @click="clean">清空<i class="el-icon-delete el-icon--right"></i></el-button>
  </el-container>
<el-container>
  <el-carousel :interval="4000" type="card" style="width: 100%" v-if="tmpflag==1" height="300px" >
    <el-carousel-item v-for="(value, key, index) in detailDic" :key="item" v-if="value.length != 0">
      <h3 class="medium">

        <el-header height="100px" style="background: darkseagreen">
        <i class="s-opportunity"></i>
          <h style="text-align: center; height: 40%" >
                {{key}}
              </h>
          </el-header>

      <el-header height="200px" style="background: powderblue">
        <h style="text-align: center; color: #F56C6C" >
                <li v-for=" v in value" > {{ v }}
                  <el-button type="primary" style="alignment: center; margin-left: 50px"
                                                           @click="addWord(v)" v-if="key=='Spell'">
                  添加到词表<i class="el-icon-plus el-icon--right"></i></el-button></li>

              </h>
      </el-header>


      </h3>

    </el-carousel-item>
  </el-carousel>
</el-container>
</el-main>


         </el-container >
      </el-container>
 </div>
</template>
 <style>
  .el-header {
    background-color: #B3C0D1;
    color: #333;
    line-height: 60px;
  }

  .el-input.is-disabled /deep/ .el-input__inner {
  color: dodgerblue;
}


</style>


<script>


import top from '../components/topNav'
export default {
  name: 'index',
  components: {
      top
  },
mounted: function(){
        this.getCurUserID()
    },
  data () {
      return {
        error_sentence: '',
        correct_sentence: '',
          detailDic: {},
        userId: 0,
        tmpflag : 0,
      }
    },
  methods: {
    getCurUserID(){
        this.$http.get('/api/getCurUserID')
                  .then((response)=>{
                    var res1 = JSON.parse(response.bodyText)
                      if(res1['err_num']==0){
                          this.userId=res1['userID'];
                          this.getCurUser()
                      }
              })
      },
      correct:function () {
        this.$http.get('/api/correctSentence?userId='+this.userId+'&orgsentences='+this.error_sentence)
          .then(function (response) {
            var res1 = JSON.parse(response.bodyText);
                    if(res1['err_num']==0){
                      this.correct_sentence = ''
                        for(var i = 0; i < res1['correctSentenceList'].length; i++){
                          this.correct_sentence += res1['correctSentenceList'][i] + '\n';
                        }
                        this.tmpflag = 1
                      this.detailDic = res1['correctDetail']

                    }
          })
      },
    clean:function(){
      this.error_sentence = ''
      this.correct_sentence = ''
      this.tmpflag = 0
    },
      addWord:function (word) {
         if(this.userId == 0){
          this.$message({type:'warning',message:"请您登陆",duration:600})
         }
         else{
           this.$http.get('/api/addWord?userId='+this.userId+'&word='+word)
             .then(function (response) {
               var res1 = JSON.parse(response.bodyText);
                    if(res1['err_num']==0){
                      this.$message({type:'success',message:"添加成功",duration:600})
                      this.correct()
                    }

             })
         }
      },
    submitUpload() {
        this.$refs.upload.submit();
      },
      handleRemove(file, fileList) {
        console.log(file, fileList);
      },
      handlePreview(file) {
        console.log(file);
      },
    handleSuccess(){
      this.$message({type:'success',message:"上传成功",duration:600})
    }
      }

}
</script>

