<template>
  <div id="list">
    <el-row style = "background: white;border-radius: 10px;border-radius: 30px;box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);" >

        <p><i class="el-icon-top"></i> {{title}}</p>
        <el-row v-for="item in itemList" :key="item.index" style="margin-top: -10px">
            <el-link :href="item.itemHref" style="color: orangered">{{ item.itemName }}</el-link>
        </el-row>
    </el-row>

  </div>
</template>

<script>

/*
 * 该文件负责显示在侧边栏的所有排行类信息，如常错类型、常用单词；
 * 其接收两个参数，一个为当前列表的标题（即“常用单词”等），另一个则为列表
 */

export default {
  name: 'list',
  props: {
      itemList: {
          type:Array
      },
      title:{
          type: String
      }
  },
  components: {
  },
  computed: {
    itemLink: function () {
      return "/search/" + this.item.itemHref
    },
  }

}
</script>

<style>

</style>
