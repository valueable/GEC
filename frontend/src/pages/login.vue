<template>
  <div id="login">
    <el-row type="flex" justify="center">
      <el-image :src= "require('@/assets/sitelogo.png')" fit="fill"></el-image>
    </el-row>

    <el-row type="flex" justify="center">
    <el-col :span="8" type="flex" justify="start">
      <el-form :model="ruleForm" status-icon :rules="rules" ref="ruleForm" label-width="100px" class="demo-ruleForm" >
        <!--用户名-->
        <el-form-item label="用户名" prop="userName">
          <el-input placeholder="请输入用户名" v-model="ruleForm.userName" autocomplete="off" clearable ></el-input>
        </el-form-item>
        <!--密码-->
        <el-form-item label="密码" prop="password" class="box">
          <el-input placeholder="请输入密码" type="password" v-model="ruleForm.password" autocomplete="off" clearable></el-input>
        </el-form-item>
        <!--登录注册按钮-->
        <el-form-item>
          <el-button type="primary" @click="submitForm('ruleForm')">登录</el-button>
          <el-button @click="gotoRegister">注册</el-button>
        </el-form-item>
</el-form>
    </el-col>
      </el-row>
    <!--返回主页按钮-->
    <el-row type="flex" justify="center">
      <el-button type="text" style="margin-left: 100px" @click="gotoHome">返回</el-button>
    </el-row>
    <br>
  </div>
</template>

<script>

export default {
  name: 'login',
  components: {
  },
  data() {
    var validateUsername = (rule, value, callback) => {
           if(!value)
          {
            callback(new Error('请输入用户名'));
          }else {
              callback();
            }
      };
    var validatePass = (rule, value, callback) => {
        if (!value) {
          callback(new Error('请输入密码'));
        } else {
          callback();
        }
      };
    return {
        ruleForm: {
          userName:'',
          password: ''
        },
      rules: {
          userName: [
            { validator: validateUsername, trigger: 'blur' }
          ],
          password: [
            { validator: validatePass, trigger: 'blur' }
          ]
        }
      };

    },
  /*created () {
    if(JSON.parse( localStorage.getItem('user')) && JSON.parse( localStorage.getItem('user')).userName){
      this.userName = JSON.parse( localStorage.getItem('user')).userName;
      this.password = JSON.parse( localStorage.getItem('user')).password;
    }
    },
*/

  methods: {
      submitForm(formName) {
        this.$refs[formName].validate((valid) => {
          if (valid) {
            var params = new URLSearchParams();
            params.append('userName', this.ruleForm.userName)
            params.append('password', this.ruleForm.password)

            this.$axios.post('/api/login/', params)
            .then(re => {
              if(re.data=='succeed'){
              window.location.href = "/index";
            }
            else{
              this.$message({type:'error',message:"用户名或密码有误！",duration:600})
            }
              })

          } else {
            console.log('error submit!!');
            return false;
          }
        });
      },
      gotoRegister(){
        window.location.href = "/register";
      },
      gotoHome(){
        window.location.href = "/index";
      }
    }
}
</script>

<style>

</style>





