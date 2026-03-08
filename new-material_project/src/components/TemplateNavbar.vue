<template>
    <!-- 模板库子导航栏 -->
    <div class="template-navbar">
        <div class="nav-items">
            <!-- 模板库首页导航 -->
            <router-link to="/template" class="nav-item" active-class="active">
                <i class="el-icon-s-home"></i>
                <span>模板库首页</span>
            </router-link>
            
            <!-- 模版创建导航 -->
            <a href="#" class="nav-item" @click.prevent="handleNavClick('create')">
                <i class="el-icon-document-add"></i>
                <span>模版创建</span>
            </a>
            
            <!-- 模板库导航 -->
            <router-link to="/templatelibrary" class="nav-item" active-class="active">
                <i class="el-icon-folder-opened"></i>
                <span>模板库</span>
            </router-link>
            
            <!-- 数据上传导航（带下拉菜单） -->
            <div class="nav-item nav-dropdown" @click="toggleUploadDropdown" ref="uploadDropdown">
                <i class="el-icon-upload"></i>
                <span>数据上传</span>
                <i class="el-icon-arrow-down dropdown-arrow" :class="{ rotated: isUploadDropdownOpen }"></i>
                
                <!-- 数据上传下拉菜单 -->
                <div class="upload-dropdown" :class="{ active: isUploadDropdownOpen }">
                    <router-link 
                       to="/upload-data"
                       class="dropdown-item"
                       @click.native="closeUploadDropdown">
                        数据上传
                    </router-link>
                    <router-link 
                       to="/create-dataset"
                       class="dropdown-item"
                       @click.native="closeUploadDropdown">
                        数据创建
                    </router-link>
                </div>
            </div>
            
            <!-- 审核管理导航（带下拉菜单）- 仅管理员可见 -->
            <div v-if="isAdmin" class="nav-item nav-dropdown" @click="toggleAuditDropdown" ref="auditDropdown">
                <i class="el-icon-s-check"></i>
                <span>审核管理</span>
                <i class="el-icon-arrow-down dropdown-arrow" :class="{ rotated: isAuditDropdownOpen }"></i>
                
                <!-- 审核管理下拉菜单 -->
                <div class="audit-dropdown" :class="{ active: isAuditDropdownOpen }">
                    <a href="#" 
                       class="dropdown-item" 
                       v-for="(item, index) in auditItems" 
                       :key="index"
                       @click.prevent="handleAuditClick(item)">
                        {{ item.text }}
                    </a>
                    <router-link 
                       to="/template-modify"
                       class="dropdown-item"
                       @click.native="isAuditDropdownOpen = false">
                        模版修改
                    </router-link>
                </div>
            </div>
            
            <!-- 机器学习导航 -->
            <router-link to="/machine-learning" class="nav-item" active-class="active">
                <i class="el-icon-data-analysis"></i>
                <span>机器学习</span>
            </router-link>
        </div>
    </div>
</template>

<script>
export default {
    name: 'TemplateNavbar',
    data() {
        return {
            isAuditDropdownOpen: false,
            isUploadDropdownOpen: false,
            auditItems: [
                { text: '模版审核', action: 'templateAudit' },
                { text: '模版停用', action: 'templateStop' }
            ]
        }
    },
    computed: {
        // 检查是否为管理员
        isAdmin() {
            // 优先从Vuex获取
            if (this.$store.getters.isAdmin) {
                return true;
            }
            // 如果Vuex中没有，从localStorage获取
            try {
                const userData = JSON.parse(localStorage.getItem('xm-user') || '{}');
                const userRole = userData.role || userData.logininfo?.type || userData.logininfo?.userType || userData.logininfo?.role || 1;
                return userRole === 2; // 2表示管理员
            } catch (error) {
                console.error('获取用户权限失败:', error);
                return false;
            }
        }
    },
    methods: {
        toggleAuditDropdown() {
            this.isAuditDropdownOpen = !this.isAuditDropdownOpen;
            this.isUploadDropdownOpen = false; // 关闭其他下拉菜单
        },
        toggleUploadDropdown() {
            this.isUploadDropdownOpen = !this.isUploadDropdownOpen;
            this.isAuditDropdownOpen = false; // 关闭其他下拉菜单
        },
        closeUploadDropdown() {
            this.isUploadDropdownOpen = false;
        },
        handleNavClick(action) {
            if (action === 'create') {
                this.$router.push('/template-create').catch(err => {
                    // 忽略导航重复错误
                    if (err.name !== 'NavigationDuplicated') {
                        throw err;
                    }
                });
            } else {
                this.$emit('nav-action', action);
            }
        },
        handleAuditClick(item) {
            this.isAuditDropdownOpen = false;
            this.$emit('audit-action', item.action);
        },
        closeDropdown(event) {
            if (this.$refs.auditDropdown && !this.$refs.auditDropdown.contains(event.target)) {
                this.isAuditDropdownOpen = false;
            }
            if (this.$refs.uploadDropdown && !this.$refs.uploadDropdown.contains(event.target)) {
                this.isUploadDropdownOpen = false;
            }
        }
    },
    mounted() {
        document.addEventListener('click', this.closeDropdown);
    },
    beforeUnmount() {
        document.removeEventListener('click', this.closeDropdown);
    }
}
</script>

<style scoped>
/* 模板库子导航栏 */
.template-navbar {
    background-color: #ffffff;
    border-bottom: 2px solid #e0e0e0;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    padding: 0 30px;
    margin-top: 80px;
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    z-index: 999;
}

.nav-items {
    display: flex;
    align-items: center;
    gap: 10px;
}

.nav-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 15px 20px;
    cursor: pointer;
    color: #333;
    font-size: 16px;
    font-weight: 500;
    transition: all 0.3s ease;
    position: relative;
    border-bottom: 3px solid transparent;
    text-decoration: none;
    white-space: nowrap;
}

.nav-item:hover,
.nav-item.active {
    color: #667eea;
    background-color: #f5f7fa;
    border-bottom-color: #667eea;
}

.nav-item i {
    font-size: 18px;
}

/* 下拉菜单样式 */
.nav-dropdown {
    position: relative;
}

.dropdown-arrow {
    font-size: 12px;
    margin-left: 4px;
    transition: transform 0.3s ease;
}

.dropdown-arrow.rotated {
    transform: rotate(180deg);
}

.audit-dropdown,
.upload-dropdown {
    position: absolute;
    top: 100%;
    left: 0;
    background-color: white;
    border-radius: 4px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    padding: 8px 0;
    min-width: 160px;
    z-index: 1000;
    margin-top: 3px;
    opacity: 0;
    visibility: hidden;
    transform: translateY(10px);
    transition: all 0.3s ease;
}

.audit-dropdown.active,
.upload-dropdown.active {
    opacity: 1;
    visibility: visible;
    transform: translateY(0);
}

.dropdown-item {
    padding: 10px 20px;
    cursor: pointer;
    color: #333;
    font-size: 14px;
    transition: all 0.2s ease;
    white-space: nowrap;
    text-decoration: none;
    display: block;
}

.dropdown-item:hover {
    background-color: #f5f7fa;
    color: #667eea;
}

.dropdown-item:not(:last-child) {
    border-bottom: 1px solid #e0e0e0;
}

/* 响应式设计 */
@media (max-width: 768px) {
    .template-navbar {
        padding: 0 10px;
    }

    .nav-item {
        padding: 12px 15px;
        font-size: 14px;
    }

    .nav-item span {
        display: none;
    }

    .nav-item i {
        font-size: 20px;
    }

    .nav-items {
        gap: 5px;
    }
}
</style>



