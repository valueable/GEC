<template>
  <div id="register" >
    <el-row type="flex" justify="center">
      <el-image :src= "require('@/assets/sitelogo.png')" fit="fill"></el-image>
    </el-row>
    <el-row type="flex" justify="center">
    <el-col :span="8" type="flex" justify="start">
  <el-form :model="ruleForm" status-icon :rules="rules" ref="ruleForm" label-width="100px" class="demo-ruleForm" >
    <el-form-item label="用户名" prop="username">
    <el-input placeholder="用户名4到16位（字母，数字，下划线，减号）组成" v-model="ruleForm.username" autocomplete="off" clearable ></el-input>
  </el-form-item>
  <el-form-item label="密码" prop="pass">
    <el-input placeholder="请输入密码" type="password" v-model="ruleForm.pass" autocomplete="off" clearable></el-input>
  </el-form-item>
  <el-form-item label="确认密码" prop="checkPass">
    <el-input placeholder="请重复输入密码" type="password" v-model="ruleForm.checkPass" autocomplete="off" clearable></el-input>
  </el-form-item>
    <el-form-item label="电子邮箱" prop="email">
    <el-input placeholder="请输入电子邮箱(非必填)" v-model="ruleForm.email" autocomplete="off" clearable ></el-input>
  </el-form-item>
    <el-form-item label="头像" prop="avater">
      <el-col :span ="10">
    <el-input placeholder="请输入链接(非必填)"  v-model="ruleForm.avater" autocomplete="off" clearable></el-input>
      </el-col>
      <el-col :span ="10">
      <el-avatar :src= "ruleForm.avater"></el-avatar>
        </el-col>
  </el-form-item>
  <el-form-item>
    <el-button type="primary" @click="submitForm('ruleForm')">注册</el-button>
    <el-button @click="resetForm('ruleForm')">重置</el-button>
  </el-form-item>
  <el-form-item>
    <el-link href="/index" type="primary">回到首页</el-link>
  </el-form-item>
</el-form>
    </el-col>
      </el-row>
  </div>

</template>

<script>

export default {
  name: 'register',
  components: {},
  data() {
      var validatePass = (rule, value, callback) => {
        if (value === '') {
          callback(new Error('请输入密码'));
        } else {
          if (this.ruleForm.checkPass !== '') {
            this.$refs.ruleForm.validateField('checkPass');
          }
          callback();
        }
      };
      var validatePass2 = (rule, value, callback) => {
        if (value === '') {
          callback(new Error('请再次输入密码'));
        } else if (value !== this.ruleForm.pass) {
          callback(new Error('两次输入密码不一致!'));
        } else {
          callback();
        }
      };
      var validateUsername = (rule, value, callback) => {
        var uPattern = /^[a-zA-Z0-9_-]{4,16}$/;
           if (!uPattern.test(value))
          {
            callback(new Error('用户名不合要求'));
          }
          else {
              callback();
            }
      };
      var validateUsernike = (rule, value, callback) => {
          if (value.length>10) {
            callback(new Error('昵称长度不能大于10'));
          } else if(value.length<=0)
          {
            callback(new Error('昵称不能为空'));
          }else {
              callback();
            }
      };
      var validatedefault = (rule, value, callback) => {
              callback();
      };
      return {
        res: '',
        ruleForm: {
          avater:'',
          nickname:'',
          username:'',
          pass: '',
          checkPass: '',
          email:'',
        sex: ''
        },
        rules: {
          sex: [
            { validator: validatedefault, trigger: 'blur' }
          ],
          avater: [
            { validator: validatedefault, trigger: 'blur' }
          ],
          email: [
            { validator: validatedefault, trigger: 'blur' }
          ],
          nickname: [
            { validator: validateUsernike, trigger: 'blur' }
          ],
          username: [
            { validator: validateUsername, trigger: 'blur' }
          ],
          pass: [
            { validator: validatePass, trigger: 'blur' }
          ],
          checkPass: [
            { validator: validatePass2, trigger: 'blur' }
          ]
        }
      };
    },
    methods: {
      submitForm(formName) {
        this.$refs[formName].validate((valid) => {
          if (valid) {

            var params = new URLSearchParams();
            params.append('userName', this.ruleForm.username);
            params.append('nickName', this.ruleForm.nickname);
            params.append('password', this.ruleForm.pass);
            params.append('sex', this.ruleForm.sex);
            params.append('email', this.ruleForm.email);
            params.append('avatar', this.ruleForm.avater);

            this.$axios.post('/api/createUser/', params)
            .then(res => {
              this.res = res
                this.$message({
                  type: 'success',
                  message: res.data
                });
              window.location.href = "/index";
            }, err => {
              this.$message({
                type: 'info',
                message: '注册失败!\n' + err
              });
            });
          } else {
            console.log('error submit!!');

            this.$message({
                type: 'success',
                message: 'error'
              });
            return false;
          }
        });
      },
      resetForm(formName) {
        this.$refs[formName].resetFields();
      }
    }
}
</script>

<style>

</style>
