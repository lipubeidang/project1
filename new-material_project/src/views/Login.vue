<template>
    <div id="app">
        <!-- 固定在顶部的导航栏 -->
        <header class="main-header">
            <div class="header-container">
                <div class="logo-container">
                    <img src="../assets/logo.png" alt="材料Logo" class="logo-img">
                    <h1 class="logo-text">生物医用材料数据资源节点</h1>
                </div>
            </div>
        </header>

        <!-- 全屏背景图片 -->
        <div class="hero-image">
            <!-- 半透明遮罩层 -->
            <div class="image-overlay"></div>

            <!-- 登录表单容器 -->
            <div class="content-wrapper">
                <div class="login-container">
                    <div class="login-box">
                        <h1 class="login-title">用户登录</h1>

                        <!-- <form @submit.prevent="handleSubmit" class="login-form" ref="formRef">
                            <div class="form-group">
                                <img src="../assets/user.png" class="form-img">
                                <input type="text" id="username" v-model="username" placeholder="请输入用户名">
                            </div>

                            <div class="form-group">
                                <img src="../assets/pass.png" class="form-img">
                                <input type="password" id="password" v-model="password" placeholder="请输入密码">
                            </div>

                            <button type="submit" class="login-btn" @click="login">登录</button>

                        </form> -->
                        <el-form ref="formRef" :model="form" class="login-form-wrapper">
                            <el-form-item prop="username">
                                <el-input prefix-icon="el-icon-user" placeholder="请输入用户名"
                                    v-model="form.username" size="large"></el-input>
                            </el-form-item>
                            <el-form-item prop="password">
                                <el-input prefix-icon="el-icon-lock" placeholder="请输入密码" show-password
                                    v-model="form.password" size="large"></el-input>
                            </el-form-item>
                            <el-form-item prop="email">
                                <el-input prefix-icon="el-icon-message" placeholder="请输入邮箱"
                                    v-model="form.email" size="large"></el-input>
                            </el-form-item>
                            <el-form-item prop="checkCode">
                                <div class="captcha-wrapper">
                                    <el-input prefix-icon="el-icon-picture" placeholder="请输入验证码"
                                        v-model="form.checkCode" size="large" class="captcha-input"></el-input>
                                    <div class="captcha-image-wrapper" @click="getCheckCode" title="点击刷新验证码">
                                        <img :src="checkCodeImage" alt="验证码" class="captcha-image" 
                                            v-if="checkCodeImage" />
                                        <div v-else class="captcha-loading">加载中...</div>
                                    </div>
                                </div>
                            </el-form-item>
                            <el-form-item>
                                <el-button type="primary" class="login-button" @click="login" size="large">登 录</el-button>
                            </el-form-item>
                        </el-form>

                        <div v-if="showSlider" class="verifybox">
                            <el-row style="margin-top:10px;">
                                <drag-verify ref="dragVerify" :width="320" :isPassing.sync="isPassing" text="请按住滑块拖动"
                                    successText="验证通过" handlerIcon="el-icon-d-arrow-right"
                                    successIcon="el-icon-circle-check" @passcallback="passcallback">
                                    <i v-show="!isPassing" slot="textBefore" class="el-icon-lock"></i>
                                </drag-verify>
                            </el-row>
                            <!-- <el-button style="margin-top:10px;margin-left:10px;" size="small" @click="reset">还原</el-button> -->
                        </div>

                        <!-- 滑块验证区域 -->
                        <!-- <div v-if="showSlider" class="slider-verify-container">
                            <p class="verify-tip">请完成安全验证</p>
                            <div class="slider-track">
                                <div class="slider-bg"></div>
                                <div class="slider-handle" @mousedown="startDrag" @touchstart="startDrag"
                                    :style="{ left: handlePosition + 'px' }">→</div>
                            </div>
                            <p class="verify-status">{{ dragText }}</p>
                        </div> -->

                        <div class="login-footer">
                            <el-button type="text" @click="open">忘记密码</el-button>
                            <router-link to="/Register">注册账号</router-link>
                        </div>
                    </div>
                </div>
            </div>


        </div>
    </div>
</template>





<script>
export default {
    name: "LoginS",
    data() {
        return {
            form: {
                username: '',
                password: '',
                email: '',
                checkCode: ''
            },
            username: '',
            password: '',
            checkCodeImage: '', // 验证码图片URL
            // 滑块验证数据
            showSlider: false,
            isDragging: false,
            vail: false,
            handlePosition: 0,
            maxPosition: 300, // 根据实际滑块轨道宽度调整
            dragText: "向右滑动验证"
        }
    },
    mounted() {
        // 页面加载时获取验证码
        this.getCheckCode();
    },
    beforeDestroy() {
        // 清理blob URL，避免内存泄漏
        if (this.checkCodeImage && this.checkCodeImage.startsWith('blob:')) {
            window.URL.revokeObjectURL(this.checkCodeImage);
        }
    },
    methods: {
        // 获取验证码
        getCheckCode() {
            // 清理旧的blob URL，避免内存泄漏
            if (this.checkCodeImage && this.checkCodeImage.startsWith('blob:')) {
                window.URL.revokeObjectURL(this.checkCodeImage);
            }
            // 添加时间戳防止缓存
            const timestamp = new Date().getTime();
            // 使用axios获取验证码图片，确保能建立session和正确的请求头
            this.$axios.get(`/api/user/checkCode?t=${timestamp}`, {
                responseType: 'blob', // 指定响应类型为blob
                withCredentials: true // 允许携带cookie，确保session能建立
            }).then(response => {
                // 将blob转换为URL
                const blob = new Blob([response.data], { type: 'image/png' });
                const url = window.URL.createObjectURL(blob);
                this.checkCodeImage = url;
            }).catch(error => {
                console.error('获取验证码失败:', error);
                this.$message.error('获取验证码失败，请刷新页面重试');
                // 如果获取失败，清空图片
                this.checkCodeImage = '';
            });
        },
        //登录
        login() {
            // console.log(this.$request);
            this.$refs['formRef'].validate((valid) => {
                if (valid) {
                    // 验证邮箱是否填写
                    if (!this.form.email || !this.form.email.trim()) {
                        this.$message.error('请输入邮箱');
                        return;
                    }
                    // 验证邮箱格式
                    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                    if (!emailRegex.test(this.form.email)) {
                        this.$message.error('请输入有效的邮箱地址');
                        return;
                    }
                    // 验证验证码是否填写
                    if (!this.form.checkCode || !this.form.checkCode.trim()) {
                        this.$message.error('请输入验证码');
                        return;
                    }
                    //验证通过
                    this.$request.post('/user/login', this.form, {
                        withCredentials: true // 允许携带cookie，确保session能传递
                    }).then(res => {
                        console.log('登录响应:', res.data); // 调试日志
                        if (res.data.msg == 'success' && res.data.logininfo) {
                            const logininfo = res.data.logininfo;
                            // 检查登录状态：1=成功, 2=用户不存在, 3=密码错误
                            if (logininfo.satus === 1) {
                                const username = logininfo.username || this.form.username;
                                // 获取用户角色：1=普通用户，2=管理员
                                // 从logininfo中获取用户类型，可能字段名为type、userType、role等
                                const userRole = logininfo.type || logininfo.userType || logininfo.role || 1; // 默认为普通用户
                                console.log('用户角色:', userRole, 'logininfo:', logininfo);
                                // 1️⃣ 保存到 Vuex
                                this.$store.commit('setUserInfo', { username, role: userRole });
                                // 2️⃣ 同步到 localStorage（防止刷新丢失）
                                // 注意：保存为 username 字段，与 TemplateCreate 等页面保持一致
                                localStorage.setItem('xm-user', JSON.stringify({ 
                                    username: username,
                                    role: userRole,
                                    logininfo: logininfo 
                                }));
                                this.$router.push('/')//跳转主页
                                this.$message.success('登陆成功')
                            } else if (logininfo.satus === 2) {
                                this.$message.error('用户不存在')
                                // 登录失败后刷新验证码
                                this.getCheckCode();
                            } else if (logininfo.satus === 3) {
                                this.$message.error('密码错误')
                                // 登录失败后刷新验证码
                                this.getCheckCode();
                            } else {
                                this.$message.error('登陆失败')
                                // 登录失败后刷新验证码
                                this.getCheckCode();
                            }
                        } else {
                            this.$message.error('登陆失败：服务器响应异常')
                            // 登录失败后刷新验证码
                            this.getCheckCode();
                        }
                    }).catch(err => {
                        console.error('登录请求失败:', err);
                        this.$message.error('登陆失败：' + (err.message || '网络错误'));
                        // 登录失败后刷新验证码
                        this.getCheckCode();
                    })
                }
            })
        },
        open() {
            this.$message('请联系管理员重置密码');
        },
        handleSubmit() {
            // 简单的验证逻辑
            if (!this.username.trim()) {
                this.$message.error('用户名不能为空');
                return;
            }
            if (!this.password.trim()) {
                this.$message.error('密码不能为空');
                return;
            }

            // 显示滑块验证
            this.showSlider = true;
        },
        //滑块验证vue
        passcallback() {
            this.$message({
                message: "验证通过",
                type: "success"
            });
            // this.isPassing = false;
            // this.showSlider = false;
            // 这里发送AJAX请求
            console.log('提交登录:', {
                username: this.username,
                password: this.password
            });
        },
        //滑块验证vue重置
        reset() {
            this.isPassing = false;
            this.$refs.dragVerify.reset()
        },
        // 滑块验证方法
        startDrag(e) {
            this.isDragging = true;
            document.addEventListener('mousemove', this.drag);
            document.addEventListener('touchmove', this.drag, { passive: false });
            document.addEventListener('mouseup', this.stopDrag);
            document.addEventListener('touchend', this.stopDrag);

            // 阻止默认行为（如页面滚动）
            e.preventDefault();
        },

        drag(e) {
            if (!this.isDragging) return;

            // 获取坐标（兼容移动端和PC端）
            const clientX = e.clientX || e.touches[0].clientX;
            const sliderTrack = document.querySelector('.slider-track');
            const rect = sliderTrack.getBoundingClientRect();

            // 计算滑块位置
            let newPos = clientX - rect.left;
            newPos = Math.max(0, Math.min(newPos, this.maxPosition - 25));

            // 更新UI
            this.handlePosition = newPos;
            document.querySelector('.slider-bg').style.width = newPos + 'px';

            // 验证通过
            if (newPos >= this.maxPosition - 30) {
                this.dragText = "验证通过 ✓";
                this.isDragging = false;
                this.vail = true;
                this.submitForm();
            }
        },

        stopDrag() {
            this.isDragging = false;
            document.removeEventListener('mousemove', this.drag);
            document.removeEventListener('touchmove', this.drag);
            if (this.vail == false) {
                // 未完成验证则重置
                if (this.handlePosition < this.maxPosition - 5) {
                    this.handlePosition = 0;
                    document.querySelector('.slider-bg').style.width = '0';
                    this.dragText = "验证失败，请重试";
                }
            }
        },
        // 实际提交表单
        submitForm() {
            // 这里发送AJAX请求
            console.log('提交登录:', {
                username: this.username,
                password: this.password
            });

            // 模拟请求成功
            setTimeout(() => {
                alert('登录成功！');
                this.resetForm();
            }, 500);
        },

        resetForm() {
            this.showSlider = false;
            this.handlePosition = 0;
            this.dragText = "向右滑动验证";
            document.querySelector('.slider-bg').style.width = '0';
        },
        handleLogin() {
            // 这里可以添加登录逻辑，比如验证用户名和密码
            // 假设登录成功后跳转到仪表盘页面
            this.$router.push({ path: '/' });
        }
    }
};
</script>
<style scoped>
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family: 'Roboto', sans-serif;
}

body {
    background-color: #f5f5f5;
    /* display: flex; */
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    /* background-image: linear-gradient(135deg, #667eea 0%, #764ba2 100%); */
}

/* 全屏背景图片样式 */
.hero-image {
    /* position: relative; */
    width: 100%;
    height: 90vh;
    background-image: url('../assets/bg.jpg');
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    display: flex;
    align-items: center;
    justify-content: center;
}

/* 图片遮罩层 */
.image-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.5);
    /* 半透明黑色遮罩 */
}

/* 内容区域调整 */
.content-wrapper {
    position: relative;
    /* 确保在遮罩层上方 */
    z-index: 1;
    width: 100%;
    max-width: 1200px;
    padding: 0 20px;
}

/* 登录表单样式调整 */
.login-container {
    width: 100%;
    max-width: 400px;
    margin: 0 auto;
    animation: fadeInUp 0.6s ease-out;
}

.login-box {
    background-color: rgba(255, 255, 255, 0.95);
    border-radius: 16px;
    padding: 50px 40px;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
    backdrop-filter: blur(10px);
}

@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(-20px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.login-title {
    text-align: center;
    margin-bottom: 40px;
    color: #333;
    font-weight: 600;
    font-size: 28px;
    letter-spacing: 1px;
}

.login-form-wrapper {
    margin-top: 20px;
}

.login-form-wrapper .el-form-item {
    margin-bottom: 24px;
}

.login-form-wrapper .el-input__inner {
    height: 48px;
    line-height: 48px;
    border-radius: 8px;
    border: 1px solid #e0e0e0;
    transition: all 0.3s ease;
}

.login-form-wrapper .el-input__inner:focus {
    border-color: #3399ff;
    box-shadow: 0 0 0 2px rgba(51, 153, 255, 0.1);
}

.captcha-wrapper {
    display: flex;
    align-items: center;
    gap: 12px;
}

.captcha-input {
    flex: 1;
}

.captcha-image-wrapper {
    cursor: pointer;
    border: 1px solid #dcdfe6;
    border-radius: 8px;
    overflow: hidden;
    transition: all 0.3s ease;
    flex-shrink: 0;
}

.captcha-image-wrapper:hover {
    border-color: #3399ff;
    box-shadow: 0 0 0 2px rgba(51, 153, 255, 0.1);
}

.captcha-image {
    width: 120px;
    height: 48px;
    display: block;
}

.captcha-loading {
    width: 120px;
    height: 48px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #909399;
    background-color: #f5f7fa;
}

.login-button {
    width: 100%;
    height: 48px;
    font-size: 16px;
    font-weight: 500;
    border-radius: 8px;
    background: linear-gradient(135deg, #3399ff 0%, #1a73e8 100%);
    border: none;
    transition: all 0.3s ease;
}

.login-button:hover {
    background: linear-gradient(135deg, #1a73e8 0%, #1557b0 100%);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(51, 153, 255, 0.4);
}

.login-form .form-group {
    margin-bottom: 20px;
    display: flex;
}

.login-form label {
    display: block;
    margin-bottom: 8px;
    color: #555;
    font-size: 14px;
}

.login-form input[type="text"],
.login-form input[type="password"] {
    width: 90%;
    padding: 12px 15px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 16px;
    transition: border-color 0.3s;
}

.login-form input[type="text"]:focus,
.login-form input[type="password"]:focus {
    border-color: #667eea;
    outline: none;
}


.login-btn {
    width: 100%;
    padding: 12px;
    background-color: #667eea;
    color: white;
    border: none;
    border-radius: 4px;
    font-size: 16px;
    cursor: pointer;
    transition: background-color 0.3s;
}

.login-btn:hover {
    background-color: #5a6fd1;
}

.error-message {
    margin-top: 15px;
    padding: 10px;
    background-color: #ffebee;
    color: #f44336;
    border-radius: 4px;
    font-size: 14px;
    text-align: center;
}

.login-footer {
    margin-top: 30px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.login-footer a,
.login-footer .el-button--text {
    color: #3399ff;
    text-decoration: none;
    font-size: 14px;
    transition: all 0.3s ease;
}

.login-footer a:hover,
.login-footer .el-button--text:hover {
    color: #1a73e8;
    text-decoration: underline;
}


/* 顶部导航栏样式 */
.main-header {
    background-color: rgb(255, 255, 255);
    color: rgb(255, 255, 255);
    width: 100%;
    position: fixed;
    top: 0;
    left: 0;
    z-index: 1000;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.header-container {
    max-width: 1200px;
    margin: 0 1%;
    /* padding: 0 0px; */
    display: flex;
    justify-content: space-between;
    align-items: center;
    height: 60px;
}

.logo-container {
    display: flex;
    align-items: center;
    gap: 15px;
}

.logo-text {
    font-size: 1.4rem;
    font-weight: 500;
    color: rgb(15, 76, 243);
}

.logo-img {
    height: 50px;
    width: auto;
}

.form-img {
    height: 44px;
    width: auto;
    margin-right: 5px;
}

/* 滑块验证样式 */
.slider-verify-container {
    width: 100%;
    padding: 20px 0;
    text-align: center;
}

.verify-tip {
    color: #666;
    margin-bottom: 15px;
}

.slider-track {
    width: 100%;
    height: 40px;
    background: #d7d6d6;
    /* border-radius: 20px; */
    position: relative;
    overflow: hidden;
}

.slider-bg {
    position: absolute;
    left: 0;
    top: 0;
    height: 100%;
    width: 0;
    background: linear-gradient(to right, #667eea, #764ba2);
    transition: width 0.3s;
}

.slider-handle {
    width: 50px;
    height: 40px;
    background: white;
    /* border-radius: 20px; */
    position: absolute;
    top: 0;
    left: 0;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: grab;
    user-select: none;
    z-index: 2;
}

.verify-status {
    margin-top: 10px;
    color: #667eea;
    font-weight: 500;
}

.captcha-modal {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
}

.captcha-box {
    background: white;
    padding: 30px;
    border-radius: 8px;
    width: 350px;
    text-align: center;
}
</style>