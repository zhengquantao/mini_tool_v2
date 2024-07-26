var page = require('webpage').create();
var system = require('system');

var file = system.args[1];
var file_type = system.args[2];
var delay = system.args[3];
var pixel_ratio = system.args[4];
var width = system.args[5];
var height = system.args[6];

var snapshot = "" + 
"    function(){"+
"        var ele = document.querySelector('div[_echarts_instance_]');"+
"        var mychart = echarts.getInstanceByDom(ele);"+
"        return mychart.getDataURL({type:'"+file_type+"', pixelRatio: " + pixel_ratio + ", excludeComponents: ['toolbox']});"+
"    }";

var snapshot_svg = "" +
"    function () {" +
"       var element = document.querySelector('div[_echarts_instance_] div');"+
"       return element.innerHTML;"+
"    }";


page.open(file, function(){
  //设置图片大小
  page.viewportSize = {
        width: width,
        height: height,
  };

  window.setTimeout(function(){
    if(file_type === 'svg'){
      var content = page.evaluateJavaScript(snapshot_svg);
    }else{
      var content = page.evaluateJavaScript(snapshot);
    }
    console.log(content);
    phantom.exit();
  }, delay);
});
