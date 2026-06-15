export interface RegionNode {
  value: string;
  label: string;
  children?: RegionNode[];
}

// Chinese administrative divisions — provinces with major cities
export const chinaRegions: RegionNode[] = [
  { value: '北京', label: '北京市', children: [
    { value: '北京-东城', label: '东城区' }, { value: '北京-西城', label: '西城区' },
    { value: '北京-朝阳', label: '朝阳区' }, { value: '北京-海淀', label: '海淀区' },
    { value: '北京-丰台', label: '丰台区' }, { value: '北京-通州', label: '通州区' },
    { value: '北京-大兴', label: '大兴区' }, { value: '北京-顺义', label: '顺义区' },
    { value: '北京-昌平', label: '昌平区' }, { value: '北京-房山', label: '房山区' },
    { value: '北京-其他', label: '其他区' },
  ]},
  { value: '上海', label: '上海市', children: [
    { value: '上海-浦东', label: '浦东新区' }, { value: '上海-嘉定', label: '嘉定区' },
    { value: '上海-宝山', label: '宝山区' }, { value: '上海-闵行', label: '闵行区' },
    { value: '上海-松江', label: '松江区' }, { value: '上海-青浦', label: '青浦区' },
    { value: '上海-奉贤', label: '奉贤区' }, { value: '上海-金山', label: '金山区' },
    { value: '上海-其他', label: '其他区' },
  ]},
  { value: '天津', label: '天津市', children: [
    { value: '天津-滨海', label: '滨海新区' }, { value: '天津-东丽', label: '东丽区' },
    { value: '天津-西青', label: '西青区' }, { value: '天津-北辰', label: '北辰区' },
    { value: '天津-武清', label: '武清区' }, { value: '天津-静海', label: '静海区' },
    { value: '天津-其他', label: '其他区' },
  ]},
  { value: '重庆', label: '重庆市', children: [
    { value: '重庆-渝北', label: '渝北区' }, { value: '重庆-江北', label: '江北区' },
    { value: '重庆-沙坪坝', label: '沙坪坝区' }, { value: '重庆-九龙坡', label: '九龙坡区' },
    { value: '重庆-南岸', label: '南岸区' }, { value: '重庆-巴南', label: '巴南区' },
    { value: '重庆-万州', label: '万州区' }, { value: '重庆-涪陵', label: '涪陵区' },
    { value: '重庆-其他', label: '其他区' },
  ]},
  { value: '广东', label: '广东省', children: [
    { value: '广东-深圳', label: '深圳市', children: [
      { value: '广东-深圳-宝安', label: '宝安区' }, { value: '广东-深圳-龙岗', label: '龙岗区' },
      { value: '广东-深圳-南山', label: '南山区' }, { value: '广东-深圳-福田', label: '福田区' },
      { value: '广东-深圳-光明', label: '光明区' }, { value: '广东-深圳-龙华', label: '龙华区' },
      { value: '广东-深圳-坪山', label: '坪山区' },
    ]},
    { value: '广东-广州', label: '广州市', children: [
      { value: '广东-广州-天河', label: '天河区' }, { value: '广东-广州-黄埔', label: '黄埔区' },
      { value: '广东-广州-番禺', label: '番禺区' }, { value: '广东-广州-花都', label: '花都区' },
      { value: '广东-广州-增城', label: '增城区' }, { value: '广东-广州-白云', label: '白云区' },
    ]},
    { value: '广东-东莞', label: '东莞市' }, { value: '广东-佛山', label: '佛山市', children: [
      { value: '广东-佛山-顺德', label: '顺德区' }, { value: '广东-佛山-南海', label: '南海区' },
      { value: '广东-佛山-禅城', label: '禅城区' }, { value: '广东-佛山-三水', label: '三水区' },
    ]},
    { value: '广东-中山', label: '中山市' }, { value: '广东-惠州', label: '惠州市' },
    { value: '广东-珠海', label: '珠海市' }, { value: '广东-江门', label: '江门市' },
    { value: '广东-肇庆', label: '肇庆市' }, { value: '广东-汕头', label: '汕头市' },
    { value: '广东-清远', label: '清远市' }, { value: '广东-河源', label: '河源市' },
    { value: '广东-阳江', label: '阳江市' }, { value: '广东-茂名', label: '茂名市' },
    { value: '广东-湛江', label: '湛江市' }, { value: '广东-其他', label: '其他' },
  ]},
  { value: '浙江', label: '浙江省', children: [
    { value: '浙江-宁波', label: '宁波市' }, { value: '浙江-杭州', label: '杭州市' },
    { value: '浙江-温州', label: '温州市' }, { value: '浙江-台州', label: '台州市' },
    { value: '浙江-嘉兴', label: '嘉兴市' }, { value: '浙江-湖州', label: '湖州市' },
    { value: '浙江-绍兴', label: '绍兴市' }, { value: '浙江-金华', label: '金华市' },
    { value: '浙江-衢州', label: '衢州市' }, { value: '浙江-丽水', label: '丽水市' },
    { value: '浙江-其他', label: '其他' },
  ]},
  { value: '江苏', label: '江苏省', children: [
    { value: '江苏-苏州', label: '苏州市' }, { value: '江苏-无锡', label: '无锡市' },
    { value: '江苏-常州', label: '常州市' }, { value: '江苏-南京', label: '南京市' },
    { value: '江苏-南通', label: '南通市' }, { value: '江苏-扬州', label: '扬州市' },
    { value: '江苏-镇江', label: '镇江市' }, { value: '江苏-泰州', label: '泰州市' },
    { value: '江苏-徐州', label: '徐州市' }, { value: '江苏-盐城', label: '盐城市' },
    { value: '江苏-其他', label: '其他' },
  ]},
  { value: '河北', label: '河北省', children: [
    { value: '河北-石家庄', label: '石家庄市' }, { value: '河北-唐山', label: '唐山市' },
    { value: '河北-保定', label: '保定市' }, { value: '河北-沧州', label: '沧州市' },
    { value: '河北-廊坊', label: '廊坊市' }, { value: '河北-邢台', label: '邢台市' },
    { value: '河北-邯郸', label: '邯郸市' }, { value: '河北-衡水', label: '衡水市' },
    { value: '河北-秦皇岛', label: '秦皇岛市' }, { value: '河北-其他', label: '其他' },
  ]},
  { value: '山东', label: '山东省', children: [
    { value: '山东-青岛', label: '青岛市' }, { value: '山东-济南', label: '济南市' },
    { value: '山东-烟台', label: '烟台市' }, { value: '山东-潍坊', label: '潍坊市' },
    { value: '山东-临沂', label: '临沂市' }, { value: '山东-淄博', label: '淄博市' },
    { value: '山东-威海', label: '威海市' }, { value: '山东-德州', label: '德州市' },
    { value: '山东-其他', label: '其他' },
  ]},
  { value: '福建', label: '福建省', children: [
    { value: '福建-厦门', label: '厦门市' }, { value: '福建-福州', label: '福州市' },
    { value: '福建-泉州', label: '泉州市' }, { value: '福建-漳州', label: '漳州市' },
    { value: '福建-莆田', label: '莆田市' }, { value: '福建-宁德', label: '宁德市' },
    { value: '福建-其他', label: '其他' },
  ]},
  { value: '湖北', label: '湖北省', children: [
    { value: '湖北-武汉', label: '武汉市' }, { value: '湖北-襄阳', label: '襄阳市' },
    { value: '湖北-宜昌', label: '宜昌市' }, { value: '湖北-荆州', label: '荆州市' },
    { value: '湖北-黄石', label: '黄石市' }, { value: '湖北-十堰', label: '十堰市' },
    { value: '湖北-其他', label: '其他' },
  ]},
  { value: '湖南', label: '湖南省', children: [
    { value: '湖南-长沙', label: '长沙市' }, { value: '湖南-株洲', label: '株洲市' },
    { value: '湖南-湘潭', label: '湘潭市' }, { value: '湖南-衡阳', label: '衡阳市' },
    { value: '湖南-岳阳', label: '岳阳市' }, { value: '湖南-常德', label: '常德市' },
    { value: '湖南-其他', label: '其他' },
  ]},
  { value: '四川', label: '四川省', children: [
    { value: '四川-成都', label: '成都市' }, { value: '四川-绵阳', label: '绵阳市' },
    { value: '四川-德阳', label: '德阳市' }, { value: '四川-宜宾', label: '宜宾市' },
    { value: '四川-南充', label: '南充市' }, { value: '四川-其他', label: '其他' },
  ]},
  { value: '河南', label: '河南省', children: [
    { value: '河南-郑州', label: '郑州市' }, { value: '河南-洛阳', label: '洛阳市' },
    { value: '河南-新乡', label: '新乡市' }, { value: '河南-南阳', label: '南阳市' },
    { value: '河南-许昌', label: '许昌市' }, { value: '河南-其他', label: '其他' },
  ]},
  { value: '安徽', label: '安徽省', children: [
    { value: '安徽-合肥', label: '合肥市' }, { value: '安徽-芜湖', label: '芜湖市' },
    { value: '安徽-马鞍山', label: '马鞍山市' }, { value: '安徽-蚌埠', label: '蚌埠市' },
    { value: '安徽-其他', label: '其他' },
  ]},
  { value: '辽宁', label: '辽宁省', children: [
    { value: '辽宁-沈阳', label: '沈阳市' }, { value: '辽宁-大连', label: '大连市' },
    { value: '辽宁-鞍山', label: '鞍山市' }, { value: '辽宁-抚顺', label: '抚顺市' },
    { value: '辽宁-其他', label: '其他' },
  ]},
  { value: '陕西', label: '陕西省', children: [
    { value: '陕西-西安', label: '西安市' }, { value: '陕西-宝鸡', label: '宝鸡市' },
    { value: '陕西-咸阳', label: '咸阳市' }, { value: '陕西-其他', label: '其他' },
  ]},
  { value: '江西', label: '江西省', children: [
    { value: '江西-南昌', label: '南昌市' }, { value: '江西-赣州', label: '赣州市' },
    { value: '江西-九江', label: '九江市' }, { value: '江西-其他', label: '其他' },
  ]},
  { value: '广西', label: '广西壮族自治区', children: [
    { value: '广西-南宁', label: '南宁市' }, { value: '广西-柳州', label: '柳州市' },
    { value: '广西-桂林', label: '桂林市' }, { value: '广西-其他', label: '其他' },
  ]},
  { value: '云南', label: '云南省', children: [
    { value: '云南-昆明', label: '昆明市' }, { value: '云南-曲靖', label: '曲靖市' },
    { value: '云南-其他', label: '其他' },
  ]},
  { value: '贵州', label: '贵州省', children: [
    { value: '贵州-贵阳', label: '贵阳市' }, { value: '贵州-遵义', label: '遵义市' },
    { value: '贵州-其他', label: '其他' },
  ]},
  { value: '山西', label: '山西省', children: [
    { value: '山西-太原', label: '太原市' }, { value: '山西-大同', label: '大同市' },
    { value: '山西-其他', label: '其他' },
  ]},
  { value: '吉林', label: '吉林省', children: [
    { value: '吉林-长春', label: '长春市' }, { value: '吉林-吉林', label: '吉林市' },
    { value: '吉林-其他', label: '其他' },
  ]},
  { value: '黑龙江', label: '黑龙江省', children: [
    { value: '黑龙江-哈尔滨', label: '哈尔滨市' }, { value: '黑龙江-大庆', label: '大庆市' },
    { value: '黑龙江-其他', label: '其他' },
  ]},
  { value: '甘肃', label: '甘肃省', children: [
    { value: '甘肃-兰州', label: '兰州市' }, { value: '甘肃-其他', label: '其他' },
  ]},
  { value: '内蒙古', label: '内蒙古自治区', children: [
    { value: '内蒙古-呼和浩特', label: '呼和浩特市' }, { value: '内蒙古-包头', label: '包头市' },
    { value: '内蒙古-其他', label: '其他' },
  ]},
  { value: '新疆', label: '新疆维吾尔自治区', children: [
    { value: '新疆-乌鲁木齐', label: '乌鲁木齐市' }, { value: '新疆-其他', label: '其他' },
  ]},
  { value: '西藏', label: '西藏自治区', children: [
    { value: '西藏-拉萨', label: '拉萨市' }, { value: '西藏-其他', label: '其他' },
  ]},
  { value: '海南', label: '海南省', children: [
    { value: '海南-海口', label: '海口市' }, { value: '海南-三亚', label: '三亚市' },
    { value: '海南-其他', label: '其他' },
  ]},
  { value: '宁夏', label: '宁夏回族自治区', children: [
    { value: '宁夏-银川', label: '银川市' }, { value: '宁夏-其他', label: '其他' },
  ]},
  { value: '青海', label: '青海省', children: [
    { value: '青海-西宁', label: '西宁市' }, { value: '青海-其他', label: '其他' },
  ]},
  { value: '香港', label: '香港特别行政区' },
  { value: '澳门', label: '澳门特别行政区' },
  { value: '台湾', label: '台湾省' },
];

// Flatten to province-city string lookup
export function findRegionByPath(path: string[]): RegionNode | undefined {
  let list = chinaRegions;
  for (const seg of path) {
    const found = list.find(r => r.value === seg);
    if (!found) return undefined;
    if (!found.children) return found;
    list = found.children;
  }
  return undefined;
}
