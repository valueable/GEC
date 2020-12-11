<template>
    <!-- data初始化为空，原来的数据以placeholder的形式给出 -->
  <div id="edituser" >
    <el-row type="flex" justify="center">
      <el-image :src= "require('@/assets/sitelogo.png')" fit="fill"></el-image>
    </el-row>
    <el-row type="flex" justify="center">
    <el-col :span="8" type="flex" justify="start">
  <el-form :model="ruleForm" status-icon :rules="rules" ref="ruleForm" label-width="100px" class="demo-ruleForm" >
    <el-form-item label="用户名" prop="username">
    <el-input  v-model="ruleForm.username" autocomplete="off" clearable ></el-input>
  </el-form-item>
  <el-form-item label="密码" prop="pass">
    <el-input placeholder="请输入密码" type="password" v-model="ruleForm.pass" autocomplete="off" clearable></el-input>
  </el-form-item>
  <el-form-item label="确认密码" prop="checkPass">
    <el-input placeholder="请重复输入密码" type="password" v-model="ruleForm.checkPass" autocomplete="off" clearable></el-input>
  </el-form-item>
    <el-form-item label="电子邮箱" prop="email">
    <el-input  v-model="ruleForm.email" autocomplete="off" clearable ></el-input>
  </el-form-item>
    <el-form-item label="头像" prop="avater">
      <el-col :span ="10">
    <el-input   v-model="ruleForm.avater" autocomplete="off" clearable></el-input>
      </el-col>
      <el-col :span ="10">
      <el-avatar :src= "ruleForm.avater"></el-avatar>
        </el-col>
  </el-form-item>
      <el-form-item label="原来的密码" prop="formalpass">
    <el-input placeholder="请输入原来的密码" type="password" v-model="ruleForm.formalpass" autocomplete="off" clearable></el-input>
  </el-form-item>
  <el-form-item>
    <el-button type="primary" @click="submitForm('ruleForm')">修改</el-button>
    <el-button @click="resetForm('ruleForm')">重置</el-button>
  </el-form-item>
</el-form>
    </el-col>
      </el-row>
  </div>

</template>

<script>

export default {
  name: 'edituser',
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
      var validatedeformalpass = (rule, value, callback) => {
        //TODO:进行以前密码的测试
        this.$http.post('/api/validatepwd/',{'userId':this.watchId,'pwd':value.toString()},{emulateJSON:true})
                  .then((response)=> {
                      var res1 = JSON.parse(response.bodyText)
                      if (res1['err_num'] == 0) {

                         callback();
                      } else {
                          callback(new Error('密码错误'));
                      }
                  });
      };
      return {
        watchId:'',
        ruleForm: {
            formalpass:'',
          avater:'',
          nikename:'',
          username:'',
          pass: '',
          checkPass: '',
          email:'',
          options: [{
          value: '男',
          label: '男'
        }, {
          value: '女',
          label: '女'
        }],
        sex: ''
        },
        rules: {
            formalpass: [
            { validator: validatedeformalpass, trigger: 'blur' }
          ],
          sex: [
            { validator: validatedefault, trigger: 'blur' }
          ],
          avater: [
            { validator: validatedefault, trigger: 'blur' }
          ],
          email: [
            { validator: validatedefault, trigger: 'blur' }
          ],
          nikename: [
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
   created: function() {
      this.getcur();

  },
    computed:{


    },

    methods: {
      submitForm(formName) {
        this.$refs[formName].validate((valid) => {
          if (valid) {

            var params = new URLSearchParams();
            params.append('userId', this.watchId);
            params.append('userName', this.ruleForm.username);
            params.append('nickName', this.ruleForm.nikename);
            params.append('password', this.ruleForm.pass);
            params.append('sex', this.ruleForm.sex);
            params.append('email', this.ruleForm.email);
            params.append('avatar', this.ruleForm.avater);

            this.$axios.post('/api/changeInfo/', params)
            .then(res => {
              if(res.data.toString() == "succeed")
              {
               alert('修改成功');
              window.location.href = "/index";
              }else{
                alert('修改失败');
            }
            });}
           else {
            console.log('修改失败');
            return false;
          }

      });},
      resetForm(formName) {
        this.$refs[formName].resetFields();
      },
      getcur: function  () {
        this.$http.get('/api/getCurUserID')
                  .then((response)=> {
                      var res1 = JSON.parse(response.bodyText);
                      if (res1['err_num'] == 0) {
                          this.watchId = res1['userID'].toString()
                      } else {
                          this.$message.error("初始化失败")
                      }
                      this.initial();
                  });
      },
      initial:function(){
        this.$http.post('/api/getUserByID/',{'userId':this.watchId},{emulateJSON:true})
              .then(function(response){
                    var res1 = JSON.parse(response.bodyText);
                    this.ruleForm.username = res1["user"][0]["fields"]["userName"];
                    // alert(res1["user"][0]["fields"]["userName"])
                    this.ruleForm.nikename = res1["user"][0]["fields"]["nickName"];
                    if (res1["user"][0]["fields"]["gender"]){
                      this.ruleForm.sex = "男"
                    }else{
                      this.ruleForm.sex = "女"
                    }
                    this.ruleForm.avater = res1["user"][0]["fields"]["avatar"];
                    this.ruleForm.email = res1["user"][0]["fields"]["email"];
              })
      }
    }
}
</script>

<style>

</style>
