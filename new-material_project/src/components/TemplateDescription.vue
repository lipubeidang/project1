<template>
  <el-dialog
    title="模板描述"
    :visible="dialogVisible"
    @update:visible="updateVisible"
    width="50%"
    :before-close="handleClose"
    :append-to-body="true"
    :close-on-click-modal="true"
    :close-on-press-escape="true"
  >
    <div class="template-description">
      <div class="description-item">
        <label>模板名称：</label>
        <span>{{ template?.name || '未知' }}</span>
      </div>
      <div class="description-item">
        <label>创建时间：</label>
        <span>{{ template?.createTime || '未知' }}</span>
      </div>
      <div class="description-item">
        <label>创建者：</label>
        <span>{{ template?.creator || '未知' }}</span>
      </div>
      <div class="description-item">
        <label>描述：</label>
        <div class="description-content">{{ template?.description || '暂无描述' }}</div>
      </div>
    </div>
    <span slot="footer" class="dialog-footer">
      <el-button @click="handleClose">关闭</el-button>
    </span>
  </el-dialog>
</template>

<script>
export default {
  name: 'TemplateDescription',
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    template: {
      type: Object,
      default: () => ({})
    }
  },
  computed: {
    dialogVisible() {
      return this.visible;
    }
  },
  methods: {
    updateVisible(value) {
      this.$emit('update:visible', value);
    },
    handleClose() {
      this.updateVisible(false);
    }
  }
}
</script>

<style scoped>
.template-description {
  padding: 20px;
}

.description-item {
  margin-bottom: 20px;
}

.description-item label {
  font-weight: bold;
  margin-right: 10px;
  color: #606266;
}

.description-content {
  margin-top: 10px;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
  min-height: 100px;
  white-space: pre-wrap;
}
</style>
