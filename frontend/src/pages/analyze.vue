<template>
  <div id="analyze">
  <TopNav></TopNav>
        <el-row>
            <el-col :span="12">
                <div id="chartPie" style="width:100%; height:400px;"></div>
            </el-col>
        </el-row>
    </div>
</template>
<script>

  import TopNav from '../components/topNav'
  import echarts from 'echarts'

    export default {
      name: 'analyze',
      components: {TopNav},
      mounted: function () {
         this.getUserID()
        },
        data() {
            return {
              userID: 0,
                 userName: '',
                chartPie: null,
              types: [],
              titles: [],
            }
        },
        methods: {
          getUserID(){
            this.$http.get('/api/getCurUserID')
                  .then((response)=>{
                    var res1 = JSON.parse(response.bodyText)
                      if(res1['err_num']==0){
                          this.userID=res1['userID'];
                          this.getUserName();
                      }
              });
          },
          getUserName(){
            this.$http.get('/api/getUserNameByID?userId='+this.userID)
                  .then((response)=>{
                    var res1 = JSON.parse(response.bodyText)
                      if(res1['err_num']==0){
                          this.userName=res1['user'];
                          this.fetchTypes()
                      }
              })
          },
          fetchTypes(){
            this.$http.get('/api/getOftenTypes?userId='+this.userID)
                  .then((response)=>{
                    var res1 = JSON.parse(response.bodyText)
                      if(res1['err_num']==0) {
                        for (var i = 0; i < res1['list'].length; i++) {
                          this.types.push({
                            'value': res1['list'][i]['fields']['error_counts'],
                            'name': res1['list'][i]['fields']['type'],
                          })
                          this.titles.push(res1['list'][i]['fields']['type'])
                        }
                        this.drawPieChart()
                      }})
          },
            drawPieChart() {
                this.chartPie = echarts.init(document.getElementById('chartPie'));
                this.chartPie.setOption({
                    title: {
                        text: this.userName+'的错误类型',
                        subtext: '错误类型占比',
                        x: 'center'
                    },
                    tooltip: {
                        trigger: 'item',
                        formatter: "{a} <br/>{b} : {c} ({d}%)"
                    },
                    legend: {
                        orient: 'vertical',
                        left: 'left',
                        data: this.titles
                    },
                    series: [
                        {
                            name: '错误类型',
                            type: 'pie',
                            radius: '55%',
                            center: ['50%', '60%'],
                            data: this.types,
                            itemStyle: {
                                emphasis: {
                                    shadowBlur: 10,
                                    shadowOffsetX: 0,
                                    shadowColor: 'rgba(0, 0, 0, 0.5)'
                                }
                            }
                        }
                    ]
                });
            },

        },

    }
</script>

<style scoped>
    .chart-container {
        width: 100%;
        float: left;
    }
    .el-col {
        padding: 30px 20px;
    }
</style>

