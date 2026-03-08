<template>
    <div id="app">
        <!-- 固定在顶部的导航栏 -->
        <header class="main-header">
            <div class="header-container">
                <div class="logo-container">
                    <img src="../assets/logo.png" alt="材料Logo" class="logo-img">
                    <h1 class="logo-text">生物医药材料管理系统</h1>
                </div>
            </div>
        </header>
        <!-- 全屏背景图片 -->
        <div class="hero-image">
            <!-- 半透明遮罩层 -->
            <div class="image-overlay"></div>
            <div class="content-wrapper">
                <div class="login-container">
                    <div class="login-box">
                        <div>
                            <el-steps :space="200" :active="active" finish-status="success" align-center>
                                <el-step title="输入学/工号"></el-step>
                                <el-step title="验证身份"></el-step>
                                <el-step title="设置密码"></el-step>
                            </el-steps>
                        </div>

                        <div v-if="showStep1">
                            <form @submit.prevent="handleSubmit1" class="login-form">
                                <div class="form-group">
                                    <img src="../assets/user.png" class="form-img">
                                    <!-- <el-input v-model="input" placeholder="请输入内容"></el-input> -->
                                    <input type="text" id="username" v-model="username" placeholder="请输入您的学/工号">
                                </div>

                                <button type="submit" class="login-btn">下一步</button>
                            </form>
                        </div>
                        <div v-if="showStep3">
                            <form @submit.prevent="handleSubmit3" class="login-form">
                                <div class="form-group">
                                    <img src="../assets/pass.png" class="form-img">
                                    <input type="password" id="password" v-model="password" placeholder="请输入新的密码">
                                </div>
                                <div class="form-group">
                                    <img src="../assets/pass.png" class="form-img">
                                    <input type="password" id="password" v-model="confirmPassword" placeholder="再次确认密码">
                                </div>
                                <router-link to="/Login">
                                    <button type="submit" class="login-btn">完成</button>
                                </router-link>
                                <!-- <button type="submit" class="login-btn">完成</button> -->
                            </form>
                        </div>

                        <div v-if="showSlider" class="verifybox">
                            <el-row style="margin-top:10px;">
                                <drag-verify ref="dragVerify" :width="350" :isPassing.sync="isPassing" text="请按住滑块拖动"
                                    successText="验证通过" handlerIcon="el-icon-d-arrow-right"
                                    successIcon="el-icon-circle-check" @passcallback="passcallback">
                                    <i v-show="!isPassing" slot="textBefore" class="el-icon-lock"></i>
                                </drag-verify>
                            </el-row>
                            <el-button style="margin-top:10px;margin-left:10px;" size="small"
                                @click="reset">还原</el-button>
                        </div>

                        <!-- 滑块验证区域 -->
                        <!-- <div v-if="showSlider" class="slider-verify-container"> -->
                        <!-- <p class="verify-tip">请完成安全验证</p>
                            <div class="slider-track">
                                <div class="slider-bg"></div>
                                <div class="slider-handle" @mousedown="startDrag" @touchstart="startDrag"
                                    :style="{ left: handlePosition + 'px' }">→</div>
                            </div>
                            <p class="verify-status">{{ dragText }}</p> -->
                        <!-- </div> -->

                    </div>
                </div>
            </div>

        </div>
    </div>
</template>



<script>
import axios from 'axios';
export default {
    name: "PasswordS",
    data() {
        return {
            active: 0,
            isPassing: false,
            username: "",
            password: "",
            confirmPassword: "",
            showStep1: true,
            showStep3: false,
            // 滑块验证数据
            showSlider: false,
            isDragging: false,
            vail: false,
            handlePosition: 0,
            maxPosition: 400, // 根据实际滑块轨道宽度调整
            dragText: "向右滑动验证"
        }
    },
    methods: {
        handleSubmit3() {
            // 简单的验证逻辑
            if (!this.password.trim()) {
                this.$message.error('密码不能为空');
                return;
            }
            if (!this.confirmPassword.trim()) {
                this.$message.error('再次确认密码');
                return;
            }
            if (this.password != this.confirmPassword) {
                this.$message.error('两次密码不一致');
                return;
            }

            this.submitForm3();
        },
        handleSubmit1() {
            // 简单的验证逻辑
            if (!this.username.trim()) {
                this.$message.error('用户名不能为空');
                return;
            }

            // 显示滑块验证
            this.showSlider = true;
        },
        next() {
            if (this.active++ > 2) this.active = 0;
        },
        //滑块验证vue
        passcallback() {
            this.$message({
                message: "验证通过",
                type: "success"
            });
            this.isPassing = false;
            this.showSlider = false;
            // 这里发送AJAX请求
            console.log('提交学工号:', {
                username: this.username
            });
            this.next();
            this.next();
            this.showStep1 = false;
            this.showStep3 = true;
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
                this.submitForm1();
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
        submitForm1() {
            // 这里发送AJAX请求
            console.log('提交学工号:', {
                username: this.username
            });

            // 模拟请求成功
            this.next();
            this.next();
            this.resetForm1();
            this.showStep1 = false;
            this.showStep3 = true;
        },

        submitForm3() {
            // 这里发送AJAX请求
            console.log('提交新密码:', {
                username: this.password
            });

            var _this = this;

            axios({
                method: "post",
                url: "http://192.168.27.118:8083/user/resetpwd",
                params: {
                    username: _this.username,
                }
            }).then(function (resp) {
                    console.log('请求成功:', resp);
                })
                .catch((error) => {
                    console.error('请求失败:', error);
                });

            // 模拟请求成功
            // this.$alert('返回首页进行登录', '密码重置成功', {
            //     confirmButtonText: '确定',
            //     callback: action => {
            //         window.location.href = 'login.html';
            //     }
            // });
        },

        resetForm1() {
            this.showSlider = false;
            this.handlePosition = 0;
            this.dragText = "向右滑动验证";
            document.querySelector('.slider-bg').style.width = '0';
        }
    }
};
</script>
<style scoped>
v.captcha-boxv {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family: 'Roboto', sans-serif;
}

/* body { */
/* background-color: #f5f5f5; */
/* display: flex; */
/* justify-content: center;
    align-items: center;
    min-height: 100vh; */
/* background-image: linear-gradient(135deg, #667eea 0%, #764ba2 100%); */
/* } */

/* 全屏背景图片样式 */
.hero-image {
    /* position: relative; */
    width: 100%;
    height: 100vh;
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
    max-width: 600px;
    margin: 0 auto;
    animation: fadeInUp 0.6s ease-out;
}

.login-box {
    background-color: rgba(255, 255, 255, 0.9);
    border-radius: 8px;
    padding: 40px;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
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
    margin-bottom: 30px;
    color: #333;
    font-weight: 500;
}

.login-form .form-group {
    margin: 20px 60px;
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
    width: 100%;
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
    width: 20%;
    margin-left: 40%;
    margin-top: 20px;
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
    margin-top: 20px;
    display: flex;
    justify-content: space-between;
}

.login-footer a {
    color: #667eea;
    text-decoration: none;
    font-size: 14px;
}

.login-footer a:hover {
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

/*滑块验证vue*/
.verifybox {
    display: flex;
    margin-left: 65px;
    padding: 20px 0;
}

/* 滑块验证样式 */
.slider-verify-container {
    width: 400px;
    margin-left: 60px;
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