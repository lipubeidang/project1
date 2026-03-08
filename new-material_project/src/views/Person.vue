<template>
  <div class="person-page">
    <Navbar1 @dropdown-action="handleDropdownAction" />
    <!-- 页面其他内容 -->
    <el-container>
      <el-aside width="300px">
        <el-row class="tac">
          <h5></h5>
          <el-menu default-active="activeIndex" class="el-menu-vertical-demo" @select="handleSelect">
            <el-menu-item index="1">
              <template slot="title">
                <i class="el-icon-s-custom"></i>
                <span slot="title" style="font-size: 18px;">基本信息</span>
              </template>
            </el-menu-item>

            <el-menu-item index="2">
              <i class="el-icon-lock"></i>
              <span slot="title" style="font-size: 18px;">重置密码</span>
            </el-menu-item>

          </el-menu>
        </el-row>
      </el-aside>

      <el-container>
        <el-main>
          <div class="flex flex-col items-center mt-10">
            <!-- 头像部分 -->
            <div class="avatar-container">
              <img :src="avatarUrl" alt="Avatar" @click="openFileInput" class="avatar-img">
              <div v-if="isHovered" class="avatar-hover-mask" @click="openFileInput">
                <p class="mask-text">更换头像</p>
              </div>
            </div>
            <!-- 隐藏的文件输入框 -->
            <input ref="fileInputRef" type="file" accept="image/*" @change="handleFileChange" class="fileInput">
            <!-- 个人信息部分 -->
            <div class="mt-20 text-center">
              <p class="text-lg font-bold">{{ name }}</p>
              <p class="text-gray-600">{{ email }}</p>
            </div>
          </div>

        </el-main>

        <el-footer>
          <div v-if="activeIndex === '1'">
            <el-form :model="ruleForm" :rules="rules1" ref="ruleForm" label-width="100px" class="demo-ruleForm">
              <!-- <el-form-item label="用户昵称" prop="name">
                <el-input v-model="ruleForm.name" prefix-icon="el-icon-user" size="large"></el-input>
              </el-form-item> -->
              <el-form-item label="姓名" prop="user">
                <el-input v-model="ruleForm.user" prefix-icon="el-icon-user-solid" size="large" disabled></el-input>
              </el-form-item>
              <el-form-item label="邮箱地址" prop="email">
                <el-input v-model="ruleForm.email" prefix-icon="el-icon-message" size="large" disabled></el-input>
              </el-form-item>
              <!-- <el-form-item>
                <el-button type="primary" @click="submitForm('ruleForm')" size="large">立即提交</el-button>
                <el-button type="success" @click="resetForm('ruleForm')" size="large" plain>重置</el-button>
              </el-form-item> -->
            </el-form>
          </div>

          <div v-if="activeIndex === '2'">
            <el-form :model="keyForm" status-icon :rules="rules2" ref="keyForm" label-width="100px"
              class="demo-keyForm">
              <el-form-item label="用户名" prop="username">
                <el-input type="text" v-model="keyForm.username" autocomplete="off" size="large"
                  prefix-icon="el-icon-lock"  disabled></el-input>
              </el-form-item>
              <el-form-item label="密码" prop="password">
                <el-input type="text" v-model="keyForm.password" autocomplete="off" size="large"
                  prefix-icon="el-icon-lock"></el-input>
              </el-form-item>
              <el-form-item label="确认密码" prop="checkPass">
                <el-input type="text" v-model="keyForm.checkPass" autocomplete="off" size="large"
                  prefix-icon="el-icon-lock"></el-input>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="submitForm('keyForm')" size="large">提交</el-button>
                <el-button @click="resetkeyForm()" size="large">取消</el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-footer>
      </el-container>
    </el-container>
  </div>
</template>

<script>
import Navbar1 from '../components/Navbar1.vue';
// import Password from './Password.vue';
export default {
  name: "PersonS",
  components: {
    Navbar1
  },
  data() {
    var validatePass = (rule, value, callback) => {
      if (value === '') {
        callback(new Error('请输入密码'));
      } else {
        if (this.keyForm.checkPass !== '') {
          this.$refs.keyForm.validateField('checkPass');
        }
        callback();
      }
    };
    var validatePass2 = (rule, value, callback) => {
      if (value === '') {
        callback(new Error('请再次输入密码'));
      } else if (value !== this.keyForm.password) {
        callback(new Error('两次输入密码不一致!'));
      } else {
        callback();
      }
    };
    return {
      // 头像链接
      avatarUrl: 'https://picsum.photos/200/200',
      // 姓名
      name: '',
      // 邮箱
      email: '',
      // 鼠标是否悬停在头像上
      isHovered: true,
      //侧边栏选择
      activeIndex: '1',
      //个人信息表单
      ruleForm: {
        name: '',
        user: '',
        email: ''
      },
      keyForm: {
        username:'',
        password: '',
        checkPass: ''
      },
      rules1: {
        // name: [
        //   { required: true, message: '请输入用户昵称', trigger: 'blur' },
        //   { min: 1, max: 5, message: '长度在 1 到 5 个字符', trigger: 'blur' }
        // ],
        user: [
          { required: true, message: '请输入用户姓名', trigger: 'blur' },
        ],
        email: [
          { required: true, message: '请输入邮箱地址', trigger: 'blur' },
        ],
      },
      rules2: {
        username: [
          { required: true, message: '请输入用户昵称', trigger: 'blur' },
        ],
        password: [
          { validator: validatePass, trigger: 'blur' },
          { min: 6, max: 18, message: '长度在 6 到 18 个字符', trigger: 'blur' }
        ],
        checkPass: [
          { validator: validatePass2, trigger: 'blur' },
          { min: 6, max: 18, message: '长度在 6 到 18 个字符', trigger: 'blur' }
        ],
      }
    };
  },
  mounted() {
    // 页面加载时获取用户信息
    this.fetchUserInfo();
  },
  methods: {
    // 获取用户信息
    fetchUserInfo() {
      // 获取当前登录的用户名
      let username = '';
      try {
        // 优先从 Vuex store 获取
        username = this.$store.state.userName;
        // 如果 Vuex 中没有，从 localStorage 获取
        if (!username) {
          const userData = JSON.parse(localStorage.getItem('xm-user') || '{}');
          username = userData.username || '';
        }
      } catch (error) {
        console.error('获取用户名失败:', error);
      }

      if (!username) {
        this.$message.warning('未获取到用户名，请先登录');
        return;
      }

      // 调用API获取用户信息
      this.$request.get(`http://localhost:8083/user/info/${username}`)
        .then(res => {
          console.log('用户信息响应:', res.data);
          console.log('完整响应对象:', res);
          
          // 处理不同的响应结构
          let userInfo = null;
          if (res.data) {
            // 如果响应有userInfo字段（注意大小写，优先检查）
            if (res.data.userInfo) {
              userInfo = res.data.userInfo;
            }
            // 如果响应有userinfo字段（小写版本）
            else if (res.data.userinfo) {
              userInfo = res.data.userinfo;
            }
            // 如果响应有data字段且msg为success
            else if (res.data.msg === 'success' && res.data.data) {
              userInfo = res.data.data;
            } 
            // 如果响应直接是用户信息对象
            else if (res.data.msg === 'success') {
              userInfo = res.data;
            }
            // 如果响应直接是用户信息（没有msg字段）
            else if (res.data.username || res.data.name) {
              userInfo = res.data;
            }
          }
          
          if (userInfo) {
            console.log('解析后的用户信息:', userInfo);
            
            // 尝试多种可能的邮箱字段名
            const email = userInfo.email || userInfo.mail || userInfo.eMail || 
                         userInfo.userEmail || userInfo.emailAddress || '';
            
            // 尝试多种可能的姓名字段名
            const name = userInfo.name || userInfo.realName || userInfo.fullName || 
                        userInfo.username || username;
            
            // 使用Vue.set确保响应式更新
            this.$set(this, 'name', name);
            this.$set(this, 'email', email);
            this.$set(this.ruleForm, 'user', name);
            this.$set(this.ruleForm, 'email', email);
            this.$set(this.keyForm, 'username', userInfo.username || username);
            
            // 如果有头像URL，更新头像
            if (userInfo.avatar || userInfo.avatarUrl || userInfo.avatar_url) {
              this.$set(this, 'avatarUrl', userInfo.avatar || userInfo.avatarUrl || userInfo.avatar_url);
            }
            
            console.log('更新后的用户信息 - 姓名:', this.name, '邮箱:', this.email);
            console.log('ruleForm.email:', this.ruleForm.email);
          } else {
            console.error('无法解析用户信息，响应数据:', res.data);
            this.$message.error('获取用户信息失败：响应格式不正确');
          }
        })
        .catch(error => {
          console.error('获取用户信息失败:', error);
          console.error('错误详情:', error.response);
          this.$message.error('获取用户信息失败，请稍后重试');
        });
    },
    // 打开文件选择框
    openFileInput() {
      this.$refs.fileInputRef.click();
    },
    // 处理文件选择
    handleFileChange(event) {
      const file = event.target.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = (e) => {
          this.avatarUrl = e.target.result;
        };
        reader.readAsDataURL(file);
      }
    },
    //提交个人信息表单
    submitForm(formName) {
      this.$refs[formName].validate((valid) => {
        // 根据表单名称选择对应的API端点和数据
        let apiUrl = '';
        let url = '';
        let formData = {};
        
        // 根据表单名称决定使用哪个API和数据
        if (formName === 'ruleForm') {
          apiUrl = '/user/updated';
          // 提取ruleForm中的必要字段
          const fieldsToSubmit = ['username', 'email']; // 根据实际需求调整
          formData = fieldsToSubmit.reduce((obj, key) => {
            if (this.ruleForm[key] !== undefined) {
              obj[key] = this.ruleForm[key];
            }
            return obj;
          }, {});
        } else if (formName === 'keyForm') {
          apiUrl = '/user/updated';
          // // 只提取keyForm中的username和password
          // const fieldsToSubmit = ['username', 'password'];
          // formData = fieldsToSubmit.reduce((obj, key) => {
          //   if (this.keyForm[key] !== undefined) {
          //     obj[key] = this.keyForm[key];
          //   }
          //   return obj;
          // }, {});
          // formData = {
          //   username: this.keyForm.username,       // 用户名
          //   password: this.keyForm.password,             // 邮箱
          // };
          const param1 = this.keyForm.username; // 参数1
          const param2 = this.keyForm.password; // 参数2
          url = `/user/updated?username=${param1}&password=${param2}`;
                  }
        
        if (valid) {
          // 验证通过，发送请求
          console.log(formData,apiUrl,url);
          // 发送请求（参数在URL中，请求体为空）
          this.$request.post(url, {}).then(res => {
            if (res.data.msg == 'success') {
              this.$router.push('/');
              this.$message.success('提交成功');
            } else {
              this.$message.error('提交失败');
            }
          }).catch(error => {
            console.error('请求失败:', error);
            this.$message.error('网络错误，请重试');
          });
          // this.$request.post(apiUrl, formData).then(res => {
          //   if (res.data.msg == 'success') {
          //     this.$router.push('/');
          //     this.$message.success('提交成功');
          //   } else {
          //     this.$message.error('提交失败');
          //   }
          // }).catch(error => {
          //   console.error('请求失败:', error);
          //   this.$message.error('网络错误，请重试');
          // });
        } else {
          console.log('表单验证失败');
          return false;
        }
      });
    },
    //重置个人信息表单
    resetForm(formName) {
      this.$refs[formName].resetFields();
    },
    //重置密码表单
    resetkeyForm() {
      // 确保数据绑定正确重置
      this.keyForm.password = '';
      this.keyForm.checkPass = '';
    },
    handleSelect(index) {
      this.activeIndex = index; // 更新选中的菜单索引
    }
  }
}
</script>

<style scoped>
/* 个人中心页面容器 */
.person-page {
    padding-top: 80px;
}

.el-aside {
  color: #4178c0;
  height: 200px;
}

.el-main {
  display: flex;
  justify-content: center;
}

.avatar-container {
  position: relative;
  cursor: pointer;
  width: 10rem;
  height: 10rem;
  border-radius: 9999px;
  /*图片圆角*/
}

.avatar-img {
  width: 10rem;
  height: 10rem;
  border-radius: 9999px;
  /*图片圆角*/
  object-fit: cover;
}

.avatar-hover-mask {
  /*掩码层*/
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
  width: 10rem;
  height: 10rem;
  background-color: rgba(0, 0, 0, 0.5);
  border-radius: 9999px;
  /*图片圆角*/
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.avatar-container:hover .avatar-hover-mask {
  /*鼠标悬停时透明度改变*/
  opacity: 1;
}

.mask-text {
  color: white;
}

.fileInput {
  display: none;
}
</style>