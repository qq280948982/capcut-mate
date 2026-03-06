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


@mcp.tool(title="创建剪映草稿", description="创建一个新的剪映草稿，支持自定义视频尺寸")
def create_draft(
    width: int = Field(default=1920, description="视频宽度"),
    height: int = Field(default=1080, description="视频高度")
) -> dict:
    """创建剪映草稿"""
    result = service.create_draft(width=width, height=height)
    draft_url = result if isinstance(result, str) else result.get("draft_url", "")
    import config
    return {"draft_url": draft_url, "tip_url": config.TIP_URL}


@mcp.tool(title="保存剪映草稿", description="保存当前草稿的修改到本地")
def save_draft(
    draft_url: str = Field(..., description="草稿URL，从create_draft返回")
) -> dict:
    """保存剪映草稿"""
    result = service.save_draft(draft_url=draft_url)
    return {"draft_url": result}


@mcp.tool(title="添加视频", description="向剪映草稿添加视频轨道和视频片段")
def add_videos(
    draft_url: str = Field(..., description="草稿URL"),
    video_infos: str = Field(..., description="视频信息JSON字符串，包含video_url、start、end等"),
    alpha: float = Field(default=1.0, description="全局透明度[0, 1]"),
    scale_x: float = Field(default=1.0, description="X轴缩放比例"),
    scale_y: float = Field(default=1.0, description="Y轴缩放比例"),
    transform_x: int = Field(default=0, description="X轴位置偏移(像素)"),
    transform_y: int = Field(default=0, description="Y轴位置偏移(像素)"),
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


@mcp.tool(title="添加音频", description="向剪映草稿添加音频轨道和音频片段")
def add_audios(
    draft_url: str = Field(..., description="草稿URL"),
    audio_infos: str = Field(..., description="音频信息JSON字符串，包含audio_url、start、end等")
) -> dict:
    """向剪映草稿批量添加音频"""
    request = AddAudiosRequest(draft_url=draft_url, audio_infos=audio_infos)
    result = service.add_audios(
        draft_url=request.draft_url, audio_infos=request.audio_infos
    )
    return {"draft_url": result[0], "track_id": result[1], "audio_ids": result[2]}


@mcp.tool(title="添加图片", description="向剪映草稿添加图片轨道和图片片段")
def add_images(
    draft_url: str = Field(..., description="草稿URL"),
    image_infos: str = Field(..., description="图片信息JSON字符串，包含img_url、start、end等"),
    alpha: float = Field(default=1.0, description="全局透明度[0, 1]"),
    scale_x: float = Field(default=1.0, description="X轴缩放比例"),
    scale_y: float = Field(default=1.0, description="Y轴缩放比例"),
    transform_x: int = Field(default=0, description="X轴位置偏移(像素)"),
    transform_y: int = Field(default=0, description="Y轴位置偏移(像素)"),
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


@mcp.tool(title="添加贴纸", description="向剪映草稿添加贴纸素材")
def add_sticker(
    draft_url: str = Field(..., description="草稿URL"),
    sticker_id: str = Field(..., description="贴纸ID，从search_sticker获取"),
    start: int = Field(default=0, description="开始时间（微秒）"),
    end: int = Field(default=5000000, description="结束时间（微秒）"),
    scale: float = Field(default=1.0, description="缩放比例"),
    transform_x: int = Field(default=0, description="X轴位置偏移(像素)"),
    transform_y: int = Field(default=0, description="Y轴位置偏移(像素)"),
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


@mcp.tool(title="添加关键帧", description="向剪映草稿中的素材添加关键帧动画")
def add_keyframes(
    draft_url: str = Field(..., description="草稿URL"),
    keyframes: str = Field(..., description="关键帧信息JSON字符串")
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


@mcp.tool(title="添加字幕", description="向剪映草稿批量添加字幕轨道和字幕片段")
def add_captions(
    draft_url: str = Field(..., description="草稿URL"),
    captions: str = Field(..., description="字幕文本JSON字符串"),
    text_color: str = Field(default="#FFFFFF", description="文字颜色(hex)"),
    border_color: str = Field(default="#000000", description="边框颜色(hex)"),
    alignment: int = Field(default=1, description="对齐方式: 0-左对齐, 1-居中, 2-右对齐"),
    alpha: float = Field(default=1.0, description="透明度[0, 1]"),
    font: str = Field(default="思源黑体", description="字体名称"),
    font_size: int = Field(default=24, description="字体大小"),
    letter_spacing: float = Field(default=0, description="字间距"),
    line_spacing: float = Field(default=1.3, description="行间距倍数"),
    scale_x: float = Field(default=1.0, description="X轴缩放"),
    scale_y: float = Field(default=1.0, description="Y轴缩放"),
    transform_x: int = Field(default=0, description="X轴偏移(像素)"),
    transform_y: int = Field(default=0, description="Y轴偏移(像素)"),
    style_text: str = Field(default="", description="富文本样式JSON字符串"),
    underline: bool = Field(default=False, description="是否添加下划线"),
    italic: bool = Field(default=False, description="是否斜体"),
    bold: bool = Field(default=False, description="是否粗体"),
    has_shadow: bool = Field(default=False, description="是否添加阴影"),
    shadow_info: Optional[Dict[str, Any]] = Field(default=None, description="阴影信息对象，包含shadow_alpha、shadow_color、shadow_diffuse、shadow_distance、shadow_angle"),
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


@mcp.tool(title="添加特效", description="向剪映草稿添加特效轨道和特效片段")
def add_effects(
    draft_url: str = Field(..., description="草稿URL"),
    effect_infos: str = Field(..., description="特效信息JSON字符串")
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
    draft_url: str = Field(..., description="草稿URL"),
    segment_ids: List[str] = Field(..., description="素材片段ID列表"),
    name: str = Field(default="线性", description="遮罩类型名称"),
    X: int = Field(default=0, description="遮罩中心X坐标（像素）"),
    Y: int = Field(default=0, description="遮罩中心Y坐标（像素）"),
    width: int = Field(default=512, description="遮罩宽度（像素）"),
    height: int = Field(default=512, description="遮罩高度（像素）"),
    feather: int = Field(default=0, description="羽化程度（0-100）"),
    rotation: int = Field(default=0, description="旋转角度（度）"),
    invert: bool = Field(default=False, description="是否反转遮罩"),
    roundCorner: int = Field(default=0, description="圆角半径（0-100）"),
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


@mcp.tool(title="添加文字样式", description="为字幕文本创建富文本样式(关键词高亮等)")
def add_text_style(
    text: str = Field(..., description="完整文本内容"),
    keyword: str = Field(default="", description="需要高亮的关键词"),
    font_size: int = Field(default=24, description="字体大小"),
    keyword_color: str = Field(default="", description="关键词颜色(hex)"),
    keyword_font_size: int = Field(default=0, description="关键词字体大小")
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


@mcp.tool(title="快速创建素材", description="快速创建包含音视频图片的素材轨道")
def easy_create_material(
    draft_url: str = Field(..., description="草稿URL"),
    audio_url: str = Field(..., description="音频文件URL"),
    text: Optional[str] = Field(default=None, description="文本内容"),
    img_url: Optional[str] = Field(default=None, description="图片URL"),
    video_url: Optional[str] = Field(default=None, description="视频URL"),
    text_color: str = Field(default="#ffffff", description="文字颜色(hex)"),
    font_size: int = Field(default=15, description="字体大小"),
    text_transform_y: int = Field(default=0, description="文字Y轴位置偏移")
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


@mcp.tool(title="获取文字动画", description="获取可用的文字出入场动画效果列表")
def get_text_animations(
    mode: int = Field(default=0, description="模式: 0-入场, 1-出场, 2-循环"),
    type: int = Field(default=0, description="类型: 0-全部")
) -> dict:
    """获取文字出入场动画"""
    request = GetTextAnimationsRequest(mode=mode, type=type)
    result = service.get_text_animations(mode=request.mode, type=request.type)
    return {"effects": result}


@mcp.tool(title="获取图片动画", description="获取可用的图片出入场动画效果列表")
def get_image_animations(
    mode: int = Field(default=0, description="模式: 0-入场, 1-出场, 2-循环"),
    type: int = Field(default=0, description="类型: 0-全部")
) -> dict:
    """获取图片出入场动画"""
    request = GetImageAnimationsRequest(mode=mode, type=type)
    result = service.get_image_animations(mode=request.mode, type=request.type)
    return {"effects": result}


@mcp.tool(title="获取草稿文件", description="获取草稿中的所有文件列表")
def get_draft(
    draft_id: str = Field(..., description="草稿ID，从draft_url中提取")
) -> dict:
    """获取草稿文件列表"""
    request = GetDraftRequest(draft_id=draft_id)
    result = service.get_draft(draft_id=request.draft_id)
    return {"files": result}


@mcp.tool(title="生成视频", description="根据草稿URL导出生成视频文件")
def gen_video(
    draft_url: str = Field(..., description="草稿URL"),
    apiKey: str = Field(default="", description="API密钥(可选)")
) -> dict:
    """生成视频 - 根据草稿URL导出视频"""
    request = GenVideoRequest(draft_url=draft_url, apiKey=apiKey)
    result = service.gen_video(draft_url=request.draft_url, apiKey=request.apiKey)
    return {"message": result}


@mcp.tool(title="查询视频生成状态", description="查询视频生成任务的当前状态")
def gen_video_status(
    draft_url: str = Field(..., description="草稿URL")
) -> dict:
    """查询视频生成任务状态"""
    request = GenVideoStatusRequest(draft_url=draft_url)
    result = service.gen_video_status(draft_url=request.draft_url)
    return result


@mcp.tool(title="获取音频时长", description="获取音频文件的时长信息")
def get_audio_duration(
    mp3_url: str = Field(..., description="音频文件URL")
) -> dict:
    """获取音频文件时长"""
    request = GetAudioDurationRequest(mp3_url=mp3_url)
    result = service.get_audio_duration(mp3_url=request.mp3_url)
    return {"duration": result}


@mcp.tool(title="计算时间线", description="根据总时长和数量计算分割后的时间线")
def timelines(
    duration: float = Field(..., description="总时长(秒)"),
    num: int = Field(default=1, description="分割数量"),
    start: float = Field(default=0, description="开始时间(秒)"),
    type: int = Field(default=0, description="类型")
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


@mcp.tool(title="音频时间线", description="根据音频文件自动计算时间线")
def audio_timelines(
    links: str = Field(..., description="音频文件URL列表JSON字符串")
) -> dict:
    """根据音频文件时长计算时间线"""
    request = AudioTimelinesRequest(links=links)
    result = service.audio_timelines(links=request.links)
    return {"timelines": result[0], "all_timelines": result[1]}


@mcp.tool(title="生成音频信息", description="根据音频URL和时间线生成音频片段信息")
def audio_infos(
    mp3_urls: str = Field(..., description="音频URL列表JSON字符串"),
    timelines_str: str = Field(..., description="时间线JSON字符串列表"),
    audio_effect: str = Field(default="", description="音频特效"),
    volume: float = Field(default=1.0, description="音量[0, 1]")
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


@mcp.tool(title="生成图片信息", description="根据图片URL和时间线生成图片片段信息")
def imgs_infos(
    imgs: str = Field(..., description="图片URL列表JSON字符串"),
    timelines_str: str = Field(..., description="时间线JSON字符串列表"),
    height: int = Field(default=1080, description="视频高度"),
    width: int = Field(default=1920, description="视频宽度"),
    in_animation: str = Field(default="", description="入场动画名称"),
    in_animation_duration: float = Field(default=0.5, description="入场动画时长"),
    loop_animation: str = Field(default="", description="循环动画名称"),
    loop_animation_duration: float = Field(default=0.5, description="循环动画时长"),
    out_animation: str = Field(default="", description="出场动画名称"),
    out_animation_duration: float = Field(default=0.5, description="出场动画时长"),
    transition: str = Field(default="", description="转场效果"),
    transition_duration: float = Field(default=0.5, description="转场时长")
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


@mcp.tool(title="生成字幕信息", description="根据文本和时间线生成字幕片段信息")
def caption_infos(
    texts: str = Field(..., description="文本内容JSON字符串"),
    timelines_str: str = Field(..., description="时间线JSON字符串列表"),
    font_size: int = Field(default=24, description="字体大小"),
    keyword_color: str = Field(default="", description="关键词颜色(hex)"),
    keyword_font_size: int = Field(default=0, description="关键词字体大小"),
    keywords: str = Field(default="", description="关键词列表JSON字符串"),
    in_animation: str = Field(default="", description="入场动画名称"),
    in_animation_duration: float = Field(default=0.5, description="入场动画时长"),
    loop_animation: str = Field(default="", description="循环动画名称"),
    loop_animation_duration: float = Field(default=0.5, description="循环动画时长"),
    out_animation: str = Field(default="", description="出场动画名称"),
    out_animation_duration: float = Field(default=0.5, description="出场动画时长"),
    transition: str = Field(default="", description="转场效果"),
    transition_duration: float = Field(default=0.5, description="转场时长")
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


@mcp.tool(title="生成特效信息", description="根据特效名称和时间线生成特效片段信息")
def effect_infos(
    effects: str = Field(..., description="特效名称JSON字符串"),
    timelines_str: str = Field(..., description="时间线JSON字符串列表")
) -> dict:
    """根据特效名称和时间线生成特效信息"""
    timelines_list = json.loads(timelines_str) if isinstance(timelines_str, str) else timelines_str
    timelines_dict = [{"start": t["start"], "end": t["end"]} for t in timelines_list]
    result = service.effect_infos(effects=effects, timelines=timelines_dict)
    return {"infos": result}


@mcp.tool(title="生成关键帧信息", description="根据关键帧类型、位置和值生成关键帧信息")
def keyframes_infos(
    ctype: str = Field(..., description="关键帧类型(如position, scale, rotation等)"),
    offsets: str = Field(..., description="位置比例JSON字符串列表"),
    values: str = Field(..., description="关键帧值JSON字符串列表"),
    segment_infos_str: str = Field(..., description="片段信息JSON字符串列表"),
    height: int = Field(default=1080, description="视频高度"),
    width: int = Field(default=1920, description="视频宽度")
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


@mcp.tool(title="生成视频信息", description="根据视频URL和时间线生成视频片段信息")
def video_infos(
    video_urls: str = Field(..., description="视频URL列表JSON字符串"),
    timelines_str: str = Field(..., description="时间线JSON字符串列表"),
    height: int = Field(default=1080, description="视频高度"),
    width: int = Field(default=1920, description="视频宽度"),
    mask: str = Field(default="", description="遮罩类型"),
    transition: str = Field(default="", description="转场效果"),
    transition_duration: float = Field(default=0.5, description="转场时长"),
    volume: float = Field(default=1.0, description="音量[0, 1]")
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


@mcp.tool(title="搜索贴纸", description="根据关键词搜索可用的贴纸素材")
def search_sticker(
    keyword: str = Field(..., description="搜索关键词")
) -> dict:
    """搜索贴纸"""
    request = SearchStickerRequest(keyword=keyword)
    result = service.search_sticker(keyword=request.keyword)
    return {"data": result}


@mcp.tool(title="提取链接", description="从文本内容中提取URL链接")
def get_url(
    output: str = Field(..., description="包含链接的文本内容")
) -> dict:
    """提取链接"""
    request = GetUrlRequest(output=output)
    result = service.get_url(output=request.output)
    return {"output": result}


@mcp.tool(title="字符串转对象列表", description="将JSON字符串列表转换为对象列表")
def str_list_to_objs(
    infos: str = Field(..., description="JSON字符串列表")
) -> dict:
    """字符串列表转化成对象列表"""
    request = StrListToObjsRequest(infos=infos)
    result = service.str_list_to_objs(infos=request.infos)
    return {"infos": result}


@mcp.tool(title="字符转列表", description="将字符串转换为字符列表")
def str_to_list(
    obj: str = Field(..., description="要转换的字符串")
) -> dict:
    """字符转列表"""
    request = StrToListRequest(obj=obj)
    result = service.str_to_list(obj=request.obj)
    return {"infos": result}


@mcp.tool(title="对象列表转字符串", description="将对象列表转换为JSON字符串列表")
def objs_to_str_list(
    outputs: str = Field(..., description="对象列表JSON字符串")
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
