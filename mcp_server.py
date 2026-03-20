from fastmcp import FastMCP
import sys
import os
import json
from pydantic import Field
from typing import List, Optional, Dict, Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src import service
from src.schemas.create_draft import CreateDraftRequest
from src.schemas.add_videos import AddVideosRequest
from src.schemas.add_audios import AddAudiosRequest
from src.schemas.add_images import AddImagesRequest
from src.schemas.add_sticker import AddStickerRequest
from src.schemas.add_keyframes import AddKeyframesRequest
from src.schemas.add_captions import AddCaptionsRequest, ShadowInfo
from src.schemas.add_effects import AddEffectsRequest
from src.schemas.add_masks import AddMasksRequest
from src.schemas.add_text_style import AddTextStyleRequest
from src.schemas.get_text_animations import GetTextAnimationsRequest
from src.schemas.get_image_animations import GetImageAnimationsRequest
from src.schemas.easy_create_material import EasyCreateMaterialRequest
from src.schemas.save_draft import SaveDraftRequest
from src.schemas.gen_video import GenVideoRequest
from src.schemas.gen_video_status import GenVideoStatusRequest
from src.schemas.get_draft import GetDraftRequest
from src.schemas.get_audio_duration import GetAudioDurationRequest
from src.schemas.timelines import TimelinesRequest
from src.schemas.audio_timelines import AudioTimelinesRequest
from src.schemas.audio_infos import AudioInfosRequest
from src.schemas.imgs_infos import ImgsInfosRequest
from src.schemas.caption_infos import CaptionInfosRequest
from src.schemas.effect_infos import EffectInfosRequest
from src.schemas.keyframes_infos import KeyframesInfosRequest
from src.schemas.video_infos import VideoInfosRequest
from src.schemas.search_sticker import SearchStickerRequest
from src.schemas.get_url import GetUrlRequest
from src.schemas.str_list_to_objs import StrListToObjsRequest
from src.schemas.str_to_list import StrToListRequest

mcp = FastMCP("CapCut Mate MCP Server")


@mcp.tool(title="创建草稿", description="创建一个新的剪映草稿，后续操作都基于此草稿进行")
def create_draft(
    width: int = Field(default=1920, ge=1, description="【必填】视频宽度分辨率，单位像素，如1920、1080，建议默认值1920"),
    height: int = Field(default=1080, ge=1, description="【必填】视频高度分辨率，单位像素，如1080、1920，建议默认值1080")
) -> dict:
    """创建剪映草稿"""
    result = service.create_draft(width=width, height=height)
    draft_url = result if isinstance(result, str) else result.get("draft_url", "")
    import config
    return {"draft_url": draft_url, "tip_url": config.TIP_URL}


@mcp.tool(title="保存剪映草稿", description="保存当前草稿的修改到本地")
def save_draft(
    draft_url: str = Field(..., description="【必填】草稿URL，从create_draft返回")
) -> dict:
    """保存剪映草稿"""
    result = service.save_draft(draft_url=draft_url)
    return {"draft_url": result}


@mcp.tool(title="添加视频", description="向剪映草稿批量添加视频轨道和视频片段。【重要】时间单位为微秒(1秒=1000000微秒)")
def add_videos(
    draft_url: str = Field(..., description="【必填】草稿URL，由create_draft返回"),
    video_infos: str = Field(..., description="""【必填】视频JSON字符串数组，格式：[{"video_url":"https://example.com/video.mp4","width":1920,"height":1080,"start":0,"end":6000000,"duration":6000000,"mask":"","transition":"","transition_duration":500000,"volume":1}]
- video_url: string, 视频文件URL地址
- width: number, 视频宽度像素
- height: number, 视频高度像素
- start: number, 视频在时间轴上的开始时间，单位微秒
- end: number, 视频在时间轴上的结束时间，单位微秒
- duration: number, 视频时长，单位微秒
- mask: string, (可选)视频蒙版，可选值：圆形、矩形、爱心、星形
- transition: string, (可选)转场效果名称
- transition_duration: number, (可选)转场时长，单位微秒
- volume: number, (可选)音量大小，范围0-10，默认1"""),
    alpha: float = Field(default=1.0, ge=0.0, le=1.0, description="【必填】全局透明度，值范围0.0-1.0，建议默认值1.0"),
    scale_x: float = Field(default=1.0, description="【必填】X轴缩放比例，1.0为原始大小，建议默认值1.0"),
    scale_y: float = Field(default=1.0, description="【必填】Y轴缩放比例，1.0为原始大小，建议默认值1.0"),
    transform_x: float = Field(default=0.0, description="【必填】X轴位置偏移，单位像素，正值向右，建议默认值0"),
    transform_y: float = Field(default=0.0, description="【必填】Y轴位置偏移，单位像素，正值向下，建议默认值0"),
    scene_timelines: str = Field(default="[]", description="""【可选】分镜时间线JSON数组，用于自动变速，格式：[{"start":0,"end":6000000,"curve_speed":"linear"}]
- start: number, 分镜开始时间
- end: number, 分镜结束时间
- curve_speed: string, 曲线变速参数"""),
) -> dict:
    """向剪映草稿添加视频"""
    request = AddVideosRequest(
        draft_url=draft_url,
        video_infos=video_infos,
        alpha=alpha,
        scale_x=scale_x,
        scale_y=scale_y,
        transform_x=transform_x,
        transform_y=transform_y,
    )
    result = service.add_videos(
        draft_url=request.draft_url,
        video_infos=request.video_infos,
        alpha=request.alpha,
        scale_x=request.scale_x,
        scale_y=request.scale_y,
        transform_x=request.transform_x,
        transform_y=request.transform_y,
    )
    return {
        "draft_url": result[0],
        "track_id": result[1],
        "video_ids": result[2],
        "segment_ids": result[3],
    }


@mcp.tool(title="添加音频", description="向剪映草稿批量添加音频轨道和音频片段。【重要】时间单位为微秒(1秒=1000000微秒)")
def add_audios(
    draft_url: str = Field(..., description="【必填】草稿URL，由create_draft返回"),
    audio_infos: str = Field(..., description="""【必填】音频JSON字符串数组，格式：[{"audio_url":"https://example.com/audio.mp3","duration":12000000,"start":0,"end":12000000,"audio_effect":"教堂"}]
- audio_url: string, 音频文件URL地址
- duration: number, 音频时长，单位微秒
- start: number, 音频在时间轴上的开始时间，单位微秒
- end: number, 音频在时间轴上的结束时间，单位微秒
- audio_effect: string, (可选)音频特效，如"教堂"、"混响"等"""),
) -> dict:
    """向剪映草稿批量添加音频"""
    request = AddAudiosRequest(draft_url=draft_url, audio_infos=audio_infos)
    result = service.add_audios(
        draft_url=request.draft_url, audio_infos=request.audio_infos
    )
    return {"draft_url": result[0], "track_id": result[1], "audio_ids": result[2]}


@mcp.tool(title="添加图片", description="向剪映草稿批量添加图片轨道和图片片段。【重要】时间单位为毫秒(1秒=1000毫秒)")
def add_images(
    draft_url: str = Field(..., description="【必填】草稿URL，由create_draft返回"),
    image_infos: str = Field(..., description="""【必填】图片JSON字符串数组，格式：[{"image_url":"https://example.com/img.png","width":1920,"height":1080,"start":0,"end":5000,"duration":5000,"animation":"淡入淡出","transition":"溶解","transition_duration":500}]
- image_url: string, 图片文件URL地址
- width: number, 图片宽度像素
- height: number, 图片高度像素
- start: number, 图片在时间轴上的开始时间，单位毫秒
- end: number, 图片在时间轴上的结束时间，单位毫秒
- duration: number, 图片显示时长，单位毫秒
- animation: string, (可选)动画效果，如"淡入淡出"
- transition: string, (可选)转场效果，如"溶解"
- transition_duration: number, (可选)转场时长，单位毫秒"""),
    alpha: float = Field(default=1.0, ge=0.0, le=1.0, description="【必填】全局透明度，值范围0.0-1.0，建议默认值1.0"),
    scale_x: float = Field(default=1.0, description="【必填】X轴缩放比例，1.0为原始大小，建议默认值1.0"),
    scale_y: float = Field(default=1.0, description="【必填】Y轴缩放比例，1.0为原始大小，建议默认值1.0"),
    transform_x: float = Field(default=0.0, description="【必填】X轴位置偏移，单位像素，正值向右，建议默认值0"),
    transform_y: float = Field(default=0.0, description="【必填】Y轴位置偏移，单位像素，正值向下，建议默认值0"),
) -> dict:
    """向剪映草稿批量添加图片"""
    request = AddImagesRequest(
        draft_url=draft_url,
        image_infos=image_infos,
        alpha=alpha,
        scale_x=scale_x,
        scale_y=scale_y,
        transform_x=transform_x,
        transform_y=transform_y,
    )
    result = service.add_images(
        draft_url=request.draft_url,
        image_infos=request.image_infos,
        alpha=request.alpha,
        scale_x=request.scale_x,
        scale_y=request.scale_y,
        transform_x=request.transform_x,
        transform_y=request.transform_y,
    )
    return {
        "draft_url": result[0],
        "track_id": result[1],
        "image_ids": result[2],
        "segment_ids": result[3],
        "segment_infos": result[4],
    }


@mcp.tool(title="添加贴纸", description="向剪映草稿添加贴纸轨道和贴纸片段。【重要】时间单位为微秒(1秒=1000000微秒)，批处理时并发要设置成1")
def add_sticker(
    draft_url: str = Field(..., description="【必填】草稿URL，由create_draft返回"),
    sticker_id: str = Field(..., description="【必填】贴纸唯一标识ID，可通过search_sticker搜索获取"),
    start: int = Field(..., description="【必填】贴纸在时间轴上的开始时间，单位微秒"),
    end: int = Field(..., description="【必填】贴纸在时间轴上的结束时间，单位微秒"),
    scale: float = Field(default=1.0, description="【必填】贴纸缩放比例，1.0为原始大小，建议默认值1.0"),
    transform_x: float = Field(default=0.0, description="【必填】X轴位置偏移，单位像素，正值向右，建议默认值0"),
    transform_y: float = Field(default=0.0, description="【必填】Y轴位置偏移，单位像素，正值向下，建议默认值0"),
) -> dict:
    """向剪映草稿添加贴纸"""
    request = AddStickerRequest(
        draft_url=draft_url,
        sticker_id=sticker_id,
        start=start,
        end=end,
        scale=scale,
        transform_x=transform_x,
        transform_y=transform_y,
    )
    result = service.add_sticker(
        draft_url=request.draft_url,
        sticker_id=request.sticker_id,
        start=request.start,
        end=request.end,
        scale=request.scale,
        transform_x=request.transform_x,
        transform_y=request.transform_y,
    )
    return {
        "draft_url": result[0],
        "sticker_id": result[1],
        "track_id": result[2],
        "segment_id": result[3],
        "duration": result[4],
    }


@mcp.tool(title="添加关键帧", description="向剪映草稿中的素材添加关键帧动画。【重要】时间单位为微秒(1秒=1000000微秒)")
def add_keyframes(
    draft_url: str = Field(..., description="【必填】草稿URL，由create_draft返回"),
    keyframes: str = Field(..., description="""【必填】关键帧JSON字符串数组，格式：[{"offset":5000000,"property":"KFTypePositionX","segment_id":"abc123","value":0.5}]
- offset: number, 关键帧时间点偏移量，通常设为片段的end值，单位微秒
- property: string, 动画属性类型，常用值：
  - KFTypePositionX: X轴位置
  - KFTypePositionY: Y轴位置  
  - KFTypeScaleX: X轴缩放
  - KFTypeScaleY: Y轴缩放
  - KFTypeRotation: 旋转角度
  - KFTypeAlpha: 透明度
- segment_id: string, 片段ID，从add_videos或add_images的返回获取
- value: number, 关键帧值，不同属性类型值范围不同"""),
) -> dict:
    """向剪映草稿添加关键帧"""
    request = AddKeyframesRequest(draft_url=draft_url, keyframes=keyframes)
    result = service.add_keyframes(
        draft_url=request.draft_url, keyframes=request.keyframes
    )
    return {
        "draft_url": result[0],
        "keyframes_added": result[1],
        "affected_segments": result[2],
    }


@mcp.tool(title="添加字幕", description="向剪映草稿批量添加字幕轨道和字幕片段。【重要】所有时间单位为微秒(1秒=1000000微秒)")
def add_captions(
    draft_url: str = Field(..., description="【必填】草稿URL，由create_draft返回"),
    captions: str = Field(..., description="""【必填】字幕JSON字符串数组，格式：[{"start":0,"end":10000000,"text":"字幕文本","keyword":"关键词","keyword_color":"#ff0000","keyword_font_size":18}]
- start: number, 开始时间，单位微秒
- end: number, 结束时间，单位微秒  
- text: string, 字幕文本内容
- keyword: string, (可选)关键词，用于高亮显示
- keyword_color: string, (可选)关键词颜色，十六进制格式如"#ff0000"
- keyword_font_size: number, (可选)关键词字体大小"""),
    text_color: str = Field(default="#ffffff", description="【必填】文字颜色，十六进制格式如#ffffff，建议默认值#ffffff"),
    border_color: str = Field(default="", description="【必填】边框颜色，十六进制格式如#000000，建议默认值空字符串（无边框）"),
    alignment: int = Field(default=1, ge=0, le=5, description="【必填】对齐方式: 0-左对齐, 1-居中, 2-右对齐, 3-左下, 4-居中, 5-右下，建议默认值1"),
    alpha: float = Field(default=1.0, ge=0.0, le=1.0, description="【必填】透明度，值范围0.0-1.0，建议默认值1.0"),
    font: str = Field(default="", description="【必填】字体名称，如'思源黑体'、'抖音体'等，建议默认值空字符串（使用草稿设置）"),
    font_size: int = Field(default=15, ge=1, description="【必填】字体大小，数值越大字越大，建议默认值15"),
    letter_spacing: float = Field(default=0.0, description="【必填】字间距，数值越大字间距越大，建议默认值0"),
    line_spacing: float = Field(default=1.0, description="【必填】行间距倍数，1.0为原始行距，建议默认值1.0"),
    scale_x: float = Field(default=1.0, description="【必填】X轴缩放比例，1.0为原始大小，建议默认值1.0"),
    scale_y: float = Field(default=1.0, description="【必填】Y轴缩放比例，1.0为原始大小，建议默认值1.0"),
    transform_x: float = Field(default=0.0, description="【必填】X轴偏移量，单位像素，正值向右，建议默认值0"),
    transform_y: float = Field(default=0.0, description="【必填】Y轴偏移量，单位像素，正值向下，建议默认值0"),
    style_text: int = Field(default=0, ge=0, le=1, description="【必填】是否使用样式文本，0-不使用，1-使用，建议默认值0"),
    underline: bool = Field(default=False, description="【必填】是否添加下划线，建议默认值False"),
    italic: bool = Field(default=False, description="【必填】是否斜体，建议默认值False"),
    bold: bool = Field(default=False, description="【必填】是否粗体，建议默认值False"),
    has_shadow: bool = Field(default=False, description="【必填】是否添加阴影，建议默认值False"),
    shadow_info: Optional[Dict[str, Any]] = Field(default=None, description="""【可选】阴影参数对象，当has_shadow为true时生效，结构：
- shadow_alpha: number, 阴影不透明度，范围0-1，默认0.9
- shadow_color: string, 阴影颜色，十六进制如"#000000"，默认#000000
- shadow_diffuse: number, 阴影扩散程度，范围0-100，默认15
- shadow_distance: number, 阴影距离，范围0-100，默认5
- shadow_angle: number, 阴影角度，范围-180到180，默认-45"""),
) -> dict:
    """向剪映草稿批量添加字幕"""
    shadow_obj = ShadowInfo(**shadow_info) if shadow_info else None
    request = AddCaptionsRequest(
        draft_url=draft_url,
        captions=captions,
        text_color=text_color,
        border_color=border_color,
        alignment=alignment,
        alpha=alpha,
        font=font,
        font_size=font_size,
        letter_spacing=letter_spacing,
        line_spacing=line_spacing,
        scale_x=scale_x,
        scale_y=scale_y,
        transform_x=transform_x,
        transform_y=transform_y,
        style_text=style_text,
        underline=underline,
        italic=italic,
        bold=bold,
        has_shadow=has_shadow,
        shadow_info=shadow_obj,
    )
    result = service.add_captions(
        draft_url=request.draft_url,
        captions=request.captions,
        text_color=request.text_color,
        border_color=request.border_color,
        alignment=request.alignment,
        alpha=request.alpha,
        font=request.font,
        font_size=request.font_size,
        letter_spacing=request.letter_spacing,
        line_spacing=request.line_spacing,
        scale_x=request.scale_x,
        scale_y=request.scale_y,
        transform_x=request.transform_x,
        transform_y=request.transform_y,
        style_text=request.style_text,
        underline=request.underline,
        italic=request.italic,
        bold=request.bold,
        has_shadow=request.has_shadow,
        shadow_info=request.shadow_info,
    )
    return {
        "draft_url": result[0],
        "track_id": result[1],
        "text_ids": result[2],
        "segment_ids": result[3],
        "segment_infos": result[4],
    }


@mcp.tool(title="添加特效", description="向剪映草稿添加特效轨道和特效片段。【重要】时间单位为微秒(1秒=1000000微秒)")
def add_effects(
    draft_url: str = Field(..., description="【必填】草稿URL，由create_draft返回"),
    effect_infos: str = Field(..., description="""【必填】特效JSON字符串数组，格式：[{"effect_title":"金粉闪闪","start":0,"end":5000000}]
- effect_title: string, 特效名称，如"金粉闪闪"、"雪花"、"录制边框III"等
- start: number, 特效开始时间，单位微秒
- end: number, 特效结束时间，单位微秒"""),
) -> dict:
    """向剪映草稿添加特效"""
    request = AddEffectsRequest(draft_url=draft_url, effect_infos=effect_infos)
    result = service.add_effects(
        draft_url=request.draft_url, effect_infos=request.effect_infos
    )
    return {
        "draft_url": result[0],
        "track_id": result[1],
        "effect_ids": result[2],
        "segment_ids": result[3],
    }


@mcp.tool(title="添加遮罩", description="向剪映草稿中的素材添加遮罩效果")
def add_masks(
    draft_url: str = Field(..., description="【必填】草稿URL，由create_draft返回"),
    segment_ids: str = Field(..., description="【必填】素材片段ID列表JSON字符串数组，格式：[\"segment_id1\",\"segment_id2\"]，从add_videos或add_images的返回值获取"),
    name: str = Field(default="线性", description="【必填】遮罩类型名称，可选值：线性、镜面、圆形、矩形、爱心、星形，建议默认值'线性'"),
    X: int = Field(default=0, description="【必填】遮罩中心X坐标，单位像素，建议默认值0"),
    Y: int = Field(default=0, description="【必填】遮罩中心Y坐标，单位像素，建议默认值0"),
    width: int = Field(default=512, description="【必填】遮罩宽度，单位像素，建议默认值512"),
    height: int = Field(default=512, description="【必填】遮罩高度，单位像素，建议默认值512"),
    feather: int = Field(default=0, ge=0, le=100, description="【必填】羽化程度，范围0-100，建议默认值0"),
    rotation: int = Field(default=0, ge=0, le=360, description="【必填】旋转角度，范围0-360度，建议默认值0"),
    invert: bool = Field(default=False, description="【必填】是否反转遮罩，true为反转，建议默认值False"),
    roundCorner: int = Field(default=0, ge=0, le=100, description="【必填】矩形圆角半径，范围0-100，建议默认值0"),
) -> dict:
    """向剪映草稿添加遮罩"""
    request = AddMasksRequest(
        draft_url=draft_url,
        segment_ids=segment_ids,
        name=name,
        X=X,
        Y=Y,
        width=width,
        height=height,
        feather=feather,
        rotation=rotation,
        invert=invert,
        roundCorner=roundCorner,
    )
    result = service.add_masks(
        draft_url=request.draft_url,
        segment_ids=request.segment_ids,
        name=request.name,
        X=request.X,
        Y=request.Y,
        width=request.width,
        height=request.height,
        feather=request.feather,
        rotation=request.rotation,
        invert=request.invert,
        roundCorner=request.roundCorner,
    )
    return {
        "draft_url": result[0],
        "masks_added": result[1],
        "affected_segments": result[2],
        "mask_ids": result[3],
    }


@mcp.tool(title="添加文本样式", description="为文本创建富文本样式，用于生成带样式的JSON文本")
def add_text_style(
    text: str = Field(..., description="【必填】完整文本内容，用于匹配和替换"),
    keyword: str = Field(..., description="【必填】需要高亮的关键词，多个用|分隔，如\"快乐|顶级思维\""),
    font_size: int = Field(default=24, ge=1, description="【必填】普通文本的字体大小，建议默认值24"),
    keyword_color: str = Field(default="#ff7100", description="【必填】关键词文本颜色，十六进制格式如#ff7100，建议默认值#ff7100"),
    keyword_font_size: int = Field(default=24, ge=1, description="【必填】关键词字体大小，建议默认值24")
) -> dict:
    """为文本创建富文本样式"""
    request = AddTextStyleRequest(
        text=text,
        keyword=keyword,
        font_size=font_size,
        keyword_color=keyword_color,
        keyword_font_size=keyword_font_size,
    )
    result = service.add_text_style(
        text=request.text,
        keyword=request.keyword,
        font_size=request.font_size,
        keyword_color=request.keyword_color,
        keyword_font_size=request.keyword_font_size,
    )
    return {"text_style": result}


@mcp.tool(title="快速创建素材", description="快速创建包含音视频图片的素材轨道，一键生成完整素材")
def easy_create_material(
    draft_url: str = Field(..., description="【必填】草稿URL，由create_draft返回"),
    audio_url: str = Field(..., description="【必填】音频文件URL地址，不能为空"),
    text: str = Field(default="", description="【必填】要添加的文字内容，建议默认值空字符串"),
    img_url: str = Field(default="", description="【必填】图片文件URL地址，建议默认值空字符串"),
    video_url: str = Field(default="", description="【必填】视频文件URL地址，建议默认值空字符串"),
    text_color: str = Field(default="#ffffff", description="【必填】文字颜色，十六进制格式如#ffffff，建议默认值#ffffff"),
    font_size: int = Field(default=15, ge=1, description="【必填】字体大小，建议默认值15"),
    text_transform_y: float = Field(default=0.0, description="【必填】文字Y轴位置偏移，单位像素，正值向下，建议默认值0.0")
) -> dict:
    """快速创建素材轨道"""
    request = EasyCreateMaterialRequest(
        draft_url=draft_url,
        audio_url=audio_url,
        text=text,
        img_url=img_url,
        video_url=video_url,
        text_color=text_color,
        font_size=font_size,
        text_transform_y=text_transform_y,
    )
    result = service.easy_create_material(
        draft_url=request.draft_url,
        audio_url=request.audio_url,
        text=request.text,
        img_url=request.img_url,
        video_url=request.video_url,
        text_color=request.text_color,
        font_size=request.font_size,
        text_transform_y=request.text_transform_y,
    )
    return {"draft_url": result}


@mcp.tool(title="获取文字动画", description="获取文字出入场动画列表，用于添加到字幕轨道")
def get_text_animations(
    mode: int = Field(default=0, ge=0, le=2, description="【必填】筛选模式：0-全部, 1-VIP, 2-免费，建议默认值0"),
    type: str = Field(default="in", description="【必填】动画类型：in-入场动画, out-出场动画, loop-循环动画，建议默认值\"in\"")
) -> dict:
    """获取文字出入场动画"""
    request = GetTextAnimationsRequest(mode=mode, type=type)
    result = service.get_text_animations(mode=request.mode, type=request.type)
    return {"effects": result}


@mcp.tool(title="获取图片动画", description="获取图片出入场动画列表，用于添加到图片轨道")
def get_image_animations(
    mode: int = Field(default=0, ge=0, le=2, description="【必填】筛选模式：0-全部, 1-VIP, 2-免费，建议默认值0"),
    type: str = Field(default="in", description="【必填】动画类型：in-入场动画, out-出场动画, loop-组合，建议默认值\"in\"")
) -> dict:
    """获取图片出入场动画"""
    request = GetImageAnimationsRequest(mode=mode, type=type)
    result = service.get_image_animations(mode=request.mode, type=request.type)
    return {"effects": result}


@mcp.tool(title="获取草稿", description="获取草稿中的文件列表和素材信息")
def get_draft(
    draft_id: str = Field(..., description="【必填】草稿ID，从draft_url中提取，如URL为 https://xxx/get_draft?draft_id=abc123，则draft_id为abc123")
) -> dict:
    """获取草稿文件列表"""
    request = GetDraftRequest(draft_id=draft_id)
    result = service.get_draft(draft_id=request.draft_id)
    return {"files": result}


@mcp.tool(title="生成视频", description="根据草稿URL导出视频，生成视频任务后返回任务ID供后续查询状态")
def gen_video(
    draft_url: str = Field(..., description="【必填】草稿URL，由create_draft返回"),
    apiKey: str = Field(..., description="【必填】API密钥，用于调用外部视频生成服务，从官网(www.jcaigc.cn)获取")
) -> dict:
    """生成视频 - 根据草稿URL导出视频"""
    request = GenVideoRequest(draft_url=draft_url, apiKey=apiKey)
    result = service.gen_video(draft_url=request.draft_url, apiKey=request.apiKey)
    return {"message": result}


@mcp.tool(title="查询视频生成状态", description="查询视频生成任务的当前状态，包括进度百分比和最终生成的视频URL")
def gen_video_status(
    draft_url: str = Field(..., description="【必填】草稿URL，由create_draft返回")
) -> dict:
    """查询视频生成任务状态"""
    request = GenVideoStatusRequest(draft_url=draft_url)
    result = service.gen_video_status(draft_url=request.draft_url)
    return result


@mcp.tool(title="获取音频时长", description="获取音频文件的时长信息，返回时长值单位为微秒")
def get_audio_duration(
    mp3_url: str = Field(..., description="【必填】音频/视频文件URL地址")
) -> dict:
    """获取音频文件时长"""
    request = GetAudioDurationRequest(mp3_url=mp3_url)
    result = service.get_audio_duration(mp3_url=request.mp3_url)
    return {"duration": result}


@mcp.tool(title="生成时间线", description="根据总时长和分割数量生成时间线数组")
def timelines(
    duration: int = Field(..., ge=0, description="【必填】总时长，单位微秒，如10000000代表10秒"),
    num: int = Field(..., ge=1, description="【必填】分割数量，即时间线上的个数"),
    start: int = Field(default=0, ge=0, description="【必填】开始偏移量，单位微秒，建议默认值0"),
    type: int = Field(default=0, ge=0, le=1, description="【必填】分割方式：0-平均分割，1-随机分割，建议默认值0")
) -> dict:
    """计算时间线"""
    request = TimelinesRequest(duration=duration, num=num, start=start, type=type)
    result = service.timelines(
        duration=request.duration,
        num=request.num,
        start=request.start,
        type=request.type,
    )
    return {"timelines": result[0], "all_timelines": result[1]}


@mcp.tool(title="音频时间线", description="根据音频文件URL列表自动计算时间线，返回每个音频的开始和结束时间")
def audio_timelines(
    links: str = Field(..., description="""【必填】音频URL JSON字符串数组，格式：["https://example.com/audio1.mp3","https://example.com/audio2.mp3"]
- 内部会自动获取每个音频的时长
- 返回的时间线数组中每个元素包含start和end时间点"""),
) -> dict:
    """根据音频文件时长计算时间线"""
    request = AudioTimelinesRequest(links=links)
    result = service.audio_timelines(links=request.links)
    return {"timelines": result[0], "all_timelines": result[1]}


@mcp.tool(title="音频信息", description="根据音频URL列表和时间线生成音频信息数组")
def audio_infos(
    mp3_urls: str = Field(..., description="""【必填】音频URL JSON字符串数组，格式：["https://example.com/audio1.mp3","https://example.com/audio2.mp3"]"""),
    timelines_str: str = Field(..., description="""【必填】时间线JSON字符串数组，格式：[{"start":0,"end":284891428},{"start":284891428,"end":579578774}]
- start: number, 开始时间，单位微秒
- end: number, 结束时间，单位微秒"""),
    audio_effect: str = Field(default="", description="【必填】音频特效名称，如\"教堂\"、\"混响\"等，建议默认值空字符串"),
    volume: float = Field(default=1.0, ge=0.0, le=10.0, description="【必填】音量大小，范围0.0-10.0，建议默认值1.0")
) -> dict:
    """根据音频URL和时间线生成音频信息"""
    timelines_list = json.loads(timelines_str) if isinstance(timelines_str, str) else timelines_str
    timelines_dict = [{"start": t["start"], "end": t["end"]} for t in timelines_list]
    result = service.audio_infos(
        mp3_urls=mp3_urls,
        timelines=timelines_dict,
        audio_effect=audio_effect,
        volume=volume,
    )
    return {"infos": result}


@mcp.tool(title="图片信息", description="根据图片URL列表和时间线生成图片信息数组，用于添加到视频轨道。【重要】时间单位为毫秒")
def imgs_infos(
    imgs: str = Field(..., description="""【必填】图片URL JSON字符串数组，格式：["https://example.com/img1.png","https://example.com/img2.png"]"""),
    timelines_str: str = Field(..., description="""【必填】时间线JSON字符串数组，格式：[{"start":0,"end":5000},{"start":5000,"end":10000}]
- start: number, 开始时间，单位毫秒
- end: number, 结束时间，单位毫秒"""),
    height: int = Field(default=1024, ge=1, description="【必填】图片高度，单位像素，建议默认值1024"),
    width: int = Field(default=1024, ge=1, description="【必填】图片宽度，单位像素，建议默认值1024"),
    in_animation: str = Field(default="", description="【必填】入场动画名称，如\"渐显出现\"、\"缩放入场\"，多个用英文|分割，建议默认值空字符串"),
    in_animation_duration: int = Field(default=500, ge=0, description="【必填】入场动画时长，单位毫秒，建议默认值500"),
    loop_animation: str = Field(default="", description="【必填】循环动画名称，多个用英文|分割，建议默认值空字符串"),
    loop_animation_duration: int = Field(default=500, ge=0, description="【必填】循环动画时长，单位毫秒，建议默认值500"),
    out_animation: str = Field(default="", description="【必填】出场动画名称，多个用英文|分割，建议默认值空字符串"),
    out_animation_duration: int = Field(default=500, ge=0, description="【必填】出场动画时长，单位毫秒，建议默认值500"),
    transition: str = Field(default="", description="【必填】转场效果名称，如\"溶解\"、\"推近\"，建议默认值空字符串"),
    transition_duration: int = Field(default=500, ge=500, le=2500, description="【必填】转场时长，单位毫秒，范围500-2500，建议默认值500")
) -> dict:
    """根据图片URL和时间线生成图片信息"""
    timelines_list = json.loads(timelines_str) if isinstance(timelines_str, str) else timelines_str
    timelines_dict = [{"start": t["start"], "end": t["end"]} for t in timelines_list]
    result = service.imgs_infos(
        imgs=imgs,
        timelines=timelines_dict,
        height=height,
        width=width,
        in_animation=in_animation,
        in_animation_duration=in_animation_duration,
        loop_animation=loop_animation,
        loop_animation_duration=loop_animation_duration,
        out_animation=out_animation,
        out_animation_duration=out_animation_duration,
        transition=transition,
        transition_duration=transition_duration,
    )
    return {"infos": result}


@mcp.tool(title="字幕信息", description="根据文本列表和时间线生成字幕信息数组，用于添加到字幕轨道。【重要】时间单位为微秒")
def caption_infos(
    texts: str = Field(..., description="""【必填】字幕文本JSON字符串数组，格式：["床前明月光","明天我发光"]"""),
    timelines_str: str = Field(..., description="""【必填】时间线JSON字符串数组，格式：[{"start":0,"end":284891428},{"start":284891428,"end":579578774}]
- start: number, 开始时间，单位微秒
- end: number, 结束时间，单位微秒"""),
    font_size: int = Field(default=24, ge=1, description="【必填】字幕字体大小，建议默认值24"),
    keyword_color: str = Field(default="#ff7100", description="【必填】关键词颜色，十六进制格式如#ff7100，建议默认值#ff7100"),
    keyword_font_size: int = Field(default=24, ge=1, description="【必填】关键词字体大小，建议默认值24"),
    keywords: str = Field(default="", description="【必填】关键词列表，多个用|分隔，如\"床前|明天\"，建议默认值空字符串"),
    in_animation: str = Field(default="", description="【必填】入场动画名称，如\"冰雪飘动\"、\"渐显入场\"，建议默认值空字符串"),
    in_animation_duration: int = Field(default=500, ge=0, description="【必填】入场动画时长，单位毫秒，建议默认值500"),
    loop_animation: str = Field(default="", description="【必填】循环动画名称，多个用英文|分割，建议默认值空字符串"),
    loop_animation_duration: int = Field(default=500, ge=0, description="【必填】循环动画时长，单位毫秒，建议默认值500"),
    out_animation: str = Field(default="", description="【必填】出场动画名称，多个用英文|分割，建议默认值空字符串"),
    out_animation_duration: int = Field(default=500, ge=0, description="【必填】出场动画时长，单位毫秒，建议默认值500"),
    transition: str = Field(default="", description="【必填】转场效果名称，建议默认值空字符串"),
    transition_duration: int = Field(default=500, ge=0, description="【必填】转场时长，单位毫秒，建议默认值500")
) -> dict:
    """根据文本和时间线生成字幕信息"""
    timelines_list = json.loads(timelines_str) if isinstance(timelines_str, str) else timelines_str
    timelines_dict = [{"start": t["start"], "end": t["end"]} for t in timelines_list]
    result = service.caption_infos(
        texts=texts,
        timelines=timelines_dict,
        font_size=font_size,
        keyword_color=keyword_color,
        keyword_font_size=keyword_font_size,
        keywords=keywords,
        in_animation=in_animation,
        in_animation_duration=in_animation_duration,
        loop_animation=loop_animation,
        loop_animation_duration=loop_animation_duration,
        out_animation=out_animation,
        out_animation_duration=out_animation_duration,
        transition=transition,
        transition_duration=transition_duration,
    )
    return {"infos": result}


@mcp.tool(title="特效信息", description="根据特效名称列表和时间线生成特效信息数组，用于添加到特效轨道")
def effect_infos(
    effects: str = Field(..., description="""【必填】特效名称JSON字符串数组，格式：["金粉闪闪","雪花"]
- 可通过get_text_animations或get_image_animations获取可用特效列表"""),
    timelines_str: str = Field(..., description="""【必填】时间线JSON字符串数组，格式：[{"start":0,"end":284891428},{"start":284891428,"end":579578774}]
- start: number, 开始时间，单位微秒
- end: number, 结束时间，单位微秒""")
) -> dict:
    """根据特效名称和时间线生成特效信息"""
    timelines_list = json.loads(timelines_str) if isinstance(timelines_str, str) else timelines_str
    timelines_dict = [{"start": t["start"], "end": t["end"]} for t in timelines_list]
    result = service.effect_infos(effects=effects, timelines=timelines_dict)
    return {"infos": result}


@mcp.tool(title="关键帧信息", description="根据关键帧类型、位置比例和值生成关键帧信息数组，用于添加到素材")
def keyframes_infos(
    ctype: str = Field(..., description="""【必填】关键帧动画属性类型，常用值：
- KFTypePositionX: X轴位置
- KFTypePositionY: Y轴位置  
- KFTypeScaleX: X轴缩放
- KFTypeScaleY: Y轴缩放
- KFTypeRotation: 旋转角度
- KFTypeAlpha: 透明度"""),
    offsets: str = Field(..., description="""【必填】位置比例JSON字符串数组，格式："0|100"或[0, 100]
- 表示关键帧在片段中的位置比例，0代表开始，100代表结束"""),
    values: str = Field(..., description="""【必填】关键帧值JSON字符串数组，格式："1|2"或[1, 2]
- 具体的动画属性值，不同属性类型值范围不同"""),
    segment_infos_str: str = Field(..., description="""【必填】片段信息JSON字符串数组，格式：[{"id":"segment_id_1","start":0,"end":5000000}]
- id: string, 片段ID
- start: number, 片段开始时间，单位微秒
- end: number, 片段结束时间，单位微秒"""),
    width: int = Field(default=1920, ge=1, description="【可选】视频宽度分辨率，单位像素，默认1920"),
    height: int = Field(default=1080, ge=1, description="【可选】视频高度分辨率，单位像素，默认1080")
) -> dict:
    """根据关键帧类型、位置比例和值生成关键帧信息"""
    segment_list = json.loads(segment_infos_str) if isinstance(segment_infos_str, str) else segment_infos_str
    segment_dict = [{"id": s["id"], "start": s["start"], "end": s["end"]} for s in segment_list]
    result = service.keyframes_infos(
        ctype=ctype,
        offsets=offsets,
        values=values,
        segment_infos=segment_dict,
        height=height,
        width=width,
    )
    return {"keyframes_infos": result}


@mcp.tool(title="视频信息", description="根据视频URL列表和时间线生成视频信息数组，用于添加到视频轨道。【重要】时间单位为微秒")
def video_infos(
    video_urls: str = Field(..., description="""【必填】视频URL JSON字符串数组，格式：["https://example.com/video1.mp4","https://example.com/video2.mp4"]"""),
    timelines_str: str = Field(..., description="""【必填】时间线JSON字符串数组，格式：[{"start":0,"end":284891428},{"start":284891428,"end":579578774}]
- start: number, 开始时间，单位微秒
- end: number, 结束时间，单位微秒"""),
    width: int = Field(default=1920, ge=1, description="【必填】视频宽度，单位像素，建议默认值1920"),
    height: int = Field(default=1080, ge=1, description="【必填】视频高度，单位像素，建议默认值1080"),
    mask: str = Field(default="", description="【必填】视频蒙版，可选值：圆形、矩形、爱心、星形，建议默认值空字符串"),
    transition: str = Field(default="", description="【必填】转场效果名称，如\"溶解\"、\"推近\"，建议默认值空字符串"),
    transition_duration: int = Field(default=1000, ge=0, description="【必填】转场时长，单位毫秒，建议默认值1000"),
    volume: float = Field(default=1.0, ge=0.0, le=10.0, description="【必填】音量大小，范围0-10，建议默认值1.0")
) -> dict:
    """根据视频URL和时间线生成视频信息"""
    timelines_list = json.loads(timelines_str) if isinstance(timelines_str, str) else timelines_str
    timelines_dict = [{"start": t["start"], "end": t["end"]} for t in timelines_list]
    result = service.video_infos(
        video_urls=video_urls,
        timelines=timelines_dict,
        height=height,
        width=width,
        mask=mask,
        transition=transition,
        transition_duration=transition_duration,
        volume=volume,
    )
    return {"infos": result}


@mcp.tool(title="搜索贴纸", description="搜索剪映贴纸素材库，返回匹配的贴纸列表包含sticker_id供add_sticker使用")
def search_sticker(
    keyword: str = Field(..., description="【必填】搜索关键词，如\"人物\"、\"爱心\"、\"表情\"等")
) -> dict:
    """搜索贴纸"""
    request = SearchStickerRequest(keyword=keyword)
    result = service.search_sticker(keyword=request.keyword)
    return {"data": result}


@mcp.tool(title="提取URL", description="从包含链接的文本中提取URL地址")
def get_url(
    output: str = Field(..., description="【必填】包含URL链接的文本内容，如\"中国人https://assets.jcaigc.cn/test1.mp3\"")
) -> dict:
    """提取链接"""
    request = GetUrlRequest(output=output)
    result = service.get_url(output=request.output)
    return {"output": result}


@mcp.tool(title="字符串列表转对象列表", description="将字符串列表转换为包含output字段的对象列表格式")
def str_list_to_objs(
    infos: str = Field(..., description="""【必填】URL字符串数组，格式：["https://example.com/file1.mp4","https://example.com/file2.mp4"]""")
) -> dict:
    """字符串列表转化成对象列表"""
    request = StrListToObjsRequest(infos=infos)
    result = service.str_list_to_objs(infos=request.infos)
    return {"infos": result}


@mcp.tool(title="字符串转列表", description="将包含JSON对象的字符串包装成数组格式")
def str_to_list(
    obj: str = Field(..., description="【必填】要转换的JSON字符串，如'{ \"infos\": [\"url1\", \"url2\"] }'")
) -> dict:
    """字符转列表"""
    request = StrToListRequest(obj=obj)
    result = service.str_to_list(obj=request.obj)
    return {"infos": result}


@mcp.tool(title="对象列表转字符串列表", description="将包含output字段的对象列表转换为纯字符串数组")
def objs_to_str_list(
    outputs: str = Field(..., description="""【必填】对象列表JSON字符串数组，格式：[{"output":"https://example.com/file1.mp4"},{"output":"https://example.com/file2.mp4"}]""")
) -> dict:
    """对象列表转化成字符串列表"""
    outputs_list = json.loads(outputs) if isinstance(outputs, str) else outputs
    result = service.objs_to_str_list(outputs=outputs_list)
    return {"infos": result}


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="CapCut Mate MCP Server")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--transport", type=str, default="http", help="Transport type (http, stdio)")
    parser.add_argument(
        "--show-help",
        action="store_true",
        help="Show this help message and available tools"
    )
    args = parser.parse_args()

    if args.show_help:
        print("""
╔════════════════════════════════════════════════════════════════╗
║           CapCut Mate MCP Server - Help                       ║
╠════════════════════════════════════════════════════════════════╣
║                                                                ║
║  Usage:                                                       ║
║    python mcp_server.py                    # HTTP mode        ║
║    python mcp_server.py --port 9000        # Custom port     ║
║    python mcp_server.py --transport stdio   # STDIO mode      ║
║                                                                ║
║  MCP Endpoint:                                                ║
║    HTTP:  http://localhost:8000/mcp                          ║
║                                                                ║
║  Available Tools (31):                                        ║
║    - create_draft          - 创建剪映草稿                     ║
║    - save_draft            - 保存剪映草稿                     ║
║    - add_videos            - 添加视频                         ║
║    - add_audios            - 添加音频                         ║
║    - add_images            - 添加图片                         ║
║    - add_sticker           - 添加贴纸                         ║
║    - add_keyframes        - 添加关键帧                        ║
║    - add_captions          - 添加字幕                         ║
║    - add_effects           - 添加特效                         ║
║    - add_masks             - 添加遮罩                         ║
║    - add_text_style       - 添加文字样式                     ║
║    - easy_create_material - 快速创建素材                     ║
║    - get_text_animations  - 获取文字动画                     ║
║    - get_image_animations - 获取图片动画                     ║
║    - get_draft            - 获取草稿文件列表                 ║
║    - gen_video            - 生成视频                          ║
║    - gen_video_status     - 查询视频生成状态                 ║
║    - get_audio_duration   - 获取音频时长                      ║
║    - timelines            - 计算时间线                        ║
║    - audio_timelines      - 音频时间线                        ║
║    - audio_infos          - 音频信息                          ║
║    - imgs_infos           - 图片信息                          ║
║    - caption_infos        - 字幕信息                          ║
║    - effect_infos         - 特效信息                          ║
║    - keyframes_infos      - 关键帧信息                        ║
║    - video_infos          - 视频信息                          ║
║    - search_sticker       - 搜索贴纸                          ║
║    - get_url              - 提取链接                          ║
║    - str_list_to_objs     - 字符串转对象                      ║
║    - str_to_list          - 字符转列表                        ║
║    - objs_to_str_list     - 对象转字符串                      ║
║                                                                ║
║  Example (Python client):                                      ║
║    from fastmcp import Client                                 ║
║    from fastmcp.client.transports import StreamableHttpTransport
║    transport = StreamableHttpTransport(url='http://localhost:8000/mcp')
║    async with Client(transport) as client:                     ║
║        result = await client.call_tool('create_draft', {})    ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
        """)
        exit(0)

    mcp.run(transport=args.transport, host=args.host, port=args.port)
