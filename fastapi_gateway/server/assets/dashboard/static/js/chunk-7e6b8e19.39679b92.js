(window["webpackJsonp"]=window["webpackJsonp"]||[]).push([["chunk-7e6b8e19"],{"60d4":function(e,t,s){},8621:function(e,t,s){"use strict";s("c891")},"87e0":function(e,t,s){},"9ed6":function(e,t,s){"use strict";s.r(t);var n=function(){var e=this,t=e.$createElement,s=e._self._c||t;return s("div",{staticClass:"login-container"},[s("el-form",{ref:"loginForm",staticClass:"login-form",attrs:{model:e.loginForm,rules:e.loginRules,autocomplete:"on","label-position":"left"}},[s("div",{staticClass:"title-container"},[s("h3",{staticClass:"title"},[e._v("FastApi GateWay")])]),s("el-form-item",{attrs:{prop:"username"}},[s("span",{staticClass:"svg-container"},[s("svg-icon",{attrs:{"icon-class":"user"}})],1),s("el-input",{ref:"username",attrs:{placeholder:"用户名",name:"username",type:"text",tabindex:"1",autocomplete:"on"},model:{value:e.loginForm.username,callback:function(t){e.$set(e.loginForm,"username",t)},expression:"loginForm.username"}})],1),s("el-tooltip",{attrs:{content:"Caps lock is On",placement:"right",manual:""},model:{value:e.capsTooltip,callback:function(t){e.capsTooltip=t},expression:"capsTooltip"}},[s("el-form-item",{attrs:{prop:"password"}},[s("span",{staticClass:"svg-container"},[s("svg-icon",{attrs:{"icon-class":"password"}})],1),s("el-input",{key:e.passwordType,ref:"password",attrs:{type:e.passwordType,placeholder:"密码",name:"password",tabindex:"2",autocomplete:"on"},on:{blur:function(t){e.capsTooltip=!1}},nativeOn:{keyup:[function(t){return e.checkCapslock(t)},function(t){return!t.type.indexOf("key")&&e._k(t.keyCode,"enter",13,t.key,"Enter")?null:e.handleLogin(t)}]},model:{value:e.loginForm.password,callback:function(t){e.$set(e.loginForm,"password",t)},expression:"loginForm.password"}}),s("span",{staticClass:"show-pwd",on:{click:e.showPwd}},[s("svg-icon",{attrs:{"icon-class":"password"===e.passwordType?"eye":"eye-open"}})],1)],1)],1),s("el-button",{staticStyle:{width:"100%","margin-bottom":"30px"},attrs:{loading:e.loading,type:"primary"},nativeOn:{click:function(t){return t.preventDefault(),e.handleLogin(t)}}},[e._v("Login")])],1),s("el-dialog",{attrs:{title:"Or connect with",visible:e.showDialog},on:{"update:visible":function(t){e.showDialog=t}}},[e._v(" Can not be simulated on local, so please combine you own business simulation! ! ! "),s("br"),s("br"),s("br"),s("social-sign")],1)],1)},o=[],a=(s("13d5"),s("d3b7"),s("b64b"),function(){var e=this,t=e.$createElement,s=e._self._c||t;return s("div",{staticClass:"social-signup-container"},[s("div",{staticClass:"sign-btn",on:{click:function(t){return e.wechatHandleClick("wechat")}}},[s("span",{staticClass:"wx-svg-container"},[s("svg-icon",{staticClass:"icon",attrs:{"icon-class":"wechat"}})],1),e._v(" WeChat ")]),s("div",{staticClass:"sign-btn",on:{click:function(t){return e.tencentHandleClick("tencent")}}},[s("span",{staticClass:"qq-svg-container"},[s("svg-icon",{staticClass:"icon",attrs:{"icon-class":"qq"}})],1),e._v(" QQ ")])])}),i=[],r={name:"SocialSignin",methods:{wechatHandleClick:function(e){alert("ok")},tencentHandleClick:function(e){alert("ok")}}},c=r,l=(s("bfec"),s("2877")),u=Object(l["a"])(c,a,i,!1,null,"7309fbbb",null),p=u.exports,d=s("5c96"),g={name:"Login",components:{SocialSign:p},data:function(){var e=function(e,t,s){t.length<6?s(new Error("密码至少为6字符")):s()};return{loginForm:{username:"",password:""},loginRules:{username:[{required:!0,trigger:"blur",message:"*请填写用户名"}],password:[{required:!0,trigger:"blur",validator:e}]},passwordType:"password",capsTooltip:!1,loading:!1,showDialog:!1,redirect:void 0,otherQuery:{}}},watch:{$route:{handler:function(e){var t=e.query;t&&(this.redirect=t.redirect,this.otherQuery=this.getOtherQuery(t))},immediate:!0}},created:function(){},mounted:function(){""===this.loginForm.username?this.$refs.username.focus():""===this.loginForm.password&&this.$refs.password.focus()},destroyed:function(){},methods:{checkCapslock:function(e){var t=e.key;this.capsTooltip=t&&1===t.length&&t>="A"&&t<="Z"},showPwd:function(){var e=this;"password"===this.passwordType?this.passwordType="":this.passwordType="password",this.$nextTick((function(){e.$refs.password.focus()}))},handleLogin:function(){var e=this;this.$refs.loginForm.validate((function(t){if(!t)return console.log("error submit!!"),!1;e.loading=!0;var s="username="+e.loginForm.username+"&password="+e.loginForm.password;e.$store.dispatch("user/login",s).then((function(){e.$router.push({path:e.redirect||"/",query:e.otherQuery}),e.loading=!1})).catch((function(t){var s=t.response;400===s.status?"LOGIN_BAD_CREDENTIALS"===s.data.message&&(t.message="您输入的用户名或密码不正确，请重新输入"):t.message="未知错误",Object(d["Message"])({message:t.message,type:"error",duration:5e3}),e.loading=!1}))}))},getOtherQuery:function(e){return Object.keys(e).reduce((function(t,s){return"redirect"!==s&&(t[s]=e[s]),t}),{})}}},m=g,f=(s("8621"),s("ea17"),Object(l["a"])(m,n,o,!1,null,"f6763fc4",null));t["default"]=f.exports},bfec:function(e,t,s){"use strict";s("87e0")},c891:function(e,t,s){},ea17:function(e,t,s){"use strict";s("60d4")}}]);