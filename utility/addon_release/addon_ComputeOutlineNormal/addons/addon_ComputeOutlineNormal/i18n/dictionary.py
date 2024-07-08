from addon_ComputeOutlineNormal.common.class_loader.auto_load import preprocess_dictionary

dictionary = {
    "zh_CN": {
        ("*", "Compute Outline Normal"): "描边法线计算",
        ("*", "No Active UV"): "目标没有UV, 无法计算",
        ("*", "Only Triangles"): "计算只支持三角形单位,目标存在多边面,请优先三角化",
        ("*", "OutlineUV already exists, and we rewrite it."): "OutlineUV已经存在,并且插件已经重写",
        ("*", "start compute"): "开始计算描边法线",
        ("*", "Outline Normal Plugin"): "描边法线插件"
    }
}

dictionary = preprocess_dictionary(dictionary)

dictionary["zh_HANS"] = dictionary["zh_CN"]
