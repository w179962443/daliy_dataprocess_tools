"""
腾讯云翻译API客户端
"""

import json
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import (
    TencentCloudSDKException,
)
from tencentcloud.tmt.v20180321 import tmt_client, models
import config


class TencentTranslator:
    """腾讯云翻译客户端"""

    def __init__(self, secret_id=None, secret_key=None):
        """
        初始化翻译客户端
        :param secret_id: 腾讯云SecretId
        :param secret_key: 腾讯云SecretKey
        """
        self.secret_id = secret_id or config.TENCENT_SECRET_ID
        self.secret_key = secret_key or config.TENCENT_SECRET_KEY

        if not self.secret_id or not self.secret_key:
            raise ValueError(
                "请配置腾讯云API密钥（TENCENT_SECRET_ID和TENCENT_SECRET_KEY）"
            )

        # 实例化认证对象
        self.cred = credential.Credential(self.secret_id, self.secret_key)

        # 实例化http选项
        httpProfile = HttpProfile()
        httpProfile.endpoint = "tmt.tencentcloudapi.com"

        # 实例化客户端配置对象
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile

        # 实例化TMT客户端
        self.client = tmt_client.TmtClient(
            self.cred, config.TENCENT_REGION, clientProfile
        )

    def translate(
        self, text, source_lang=None, target_lang=None, untranslated_text=None
    ):
        """
        翻译文本
        :param text: 待翻译的文本
        :param source_lang: 源语言，默认使用配置文件中的设置
        :param target_lang: 目标语言，默认使用配置文件中的设置
        :param untranslated_text: 不希望被翻译的文本内容
        :return: 翻译结果字典 {'target_text': '翻译后的文本', 'source': '源语言', 'target': '目标语言', 'used_amount': 字符数}
        """
        try:
            # 去除首尾空白
            text = text.strip()
            if not text:
                return {
                    "target_text": "",
                    "source": "",
                    "target": "",
                    "used_amount": 0,
                    "error": "文本为空",
                }

            # 实例化请求对象
            req = models.TextTranslateRequest()
            params = {
                "SourceText": text,
                "Source": source_lang or config.SOURCE_LANG,
                "Target": target_lang or config.TARGET_LANG,
                "ProjectId": config.TENCENT_PROJECT_ID,
            }

            # 添加不翻译文本（如果有）
            if untranslated_text:
                params["UntranslatedText"] = untranslated_text

            req.from_json_string(json.dumps(params))

            # 发起请求
            resp = self.client.TextTranslate(req)

            # 解析响应
            result = {
                "target_text": resp.TargetText,
                "source": resp.Source,
                "target": resp.Target,
                "used_amount": resp.UsedAmount if hasattr(resp, "UsedAmount") else 0,
                "error": None,
            }

            return result

        except TencentCloudSDKException as err:
            return {
                "target_text": "",
                "source": "",
                "target": "",
                "used_amount": 0,
                "error": f"翻译API错误: {err}",
            }
        except Exception as e:
            return {
                "target_text": "",
                "source": "",
                "target": "",
                "used_amount": 0,
                "error": f"未知错误: {e}",
            }


# 测试代码
if __name__ == "__main__":
    # 设置环境变量后测试
    try:
        translator = TencentTranslator()
        result = translator.translate("Hello, world!")
        print(f"翻译结果: {result}")
    except ValueError as e:
        print(f"错误: {e}")
        print("请设置环境变量 TENCENT_SECRET_ID 和 TENCENT_SECRET_KEY")
