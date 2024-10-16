from addon_ComputeOutlineNormal.common.class_loader.auto_load import preprocess_dictionary

dictionary = {
    "zh_CN": {
        ("*", "Compute Outline Normal"): "描边法线计算",
        ("*", "No MainUV"): "目标没有MainUV,无法计算描边法线",
        ("*", "OutlineUV already exists, and we rewrite it."): "OutlineUV已经存在,并且已经重写",
        ("*", "start compute"): "开始计算描边法线",
        ("*", "Outline Normal Plugin"): "描边法线插件"
    }
}

dictionary = preprocess_dictionary(dictionary)

dictionary["zh_HANS"] = dictionary["zh_CN"]
