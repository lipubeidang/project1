import React, { useState, useEffect, useRef } from 'https://cdn.jsdelivr.net/npm/react@18.2.0/+esm';
import reactDom from 'https://cdn.jsdelivr.net/npm/react-dom@18.2.0/+esm';


function CustomWidget() {
	const [inputValue, setInputValue] = useState(""); // 用户输入
	const [conversation, setConversation] = useState([]); // 对话历史
	const [isLoading, setIsLoading] = useState(false); // 加载状态
	const [isEditingFeedback, setIsEditingFeedback] = useState(false); // 是否正在编辑评价
	const chatEndRef = useRef(null); // 用于指向聊天区域底部的引用

	// 处理用户输入
	const handleInputChange = (e) => {
		setInputValue(e.target.value);
	};

	// 自动滚动到底部
	const scrollToBottom = () => {
		if (chatEndRef.current) {
			chatEndRef.current.scrollIntoView({ behavior: "smooth" });
		}
	};

	// 每次对话更新后，滚动到底部（仅在未编辑反馈时）
	useEffect(() => {
		if (!isEditingFeedback) {
			scrollToBottom();
		}
	}, [conversation]);

	// 处理 API 调用
	const callApi = async () => {
		if (!inputValue.trim() || isLoading) return; // 如果输入为空或正在加载，直接返回

		setIsLoading(true); // 开始加载

		// 将用户输入添加到对话历史
		setConversation(prev => [...prev, { type: 'user', text: inputValue }]);

		try {
			// 调用外部 API
			const url = `http://192.168.25.10:32250/generate?user_input=${encodeURIComponent(inputValue)}`;
			const response = await fetch(url);
			if (!response.ok) {
				throw new Error('API call failed');
			}

			const data = await response.json(); // 解析响应数据
			console.log(data.chat_history);
			// 将AI回复添加到对话历史
			const bot_response = data.response || "No response from API";
			setConversation(prev => [
				...prev,
				{
					type: 'ai',
					text: bot_response,
					rating: 0, // 初始评分为0
					feedback: "", // 初始反馈为空
					showFeedback: true, // 显示反馈部分
					callApiState:'success'
				}
			]);
		} catch (error) {
			console.error('API call failed:', error);
			setConversation(prev => [
				...prev,
				{
					type: 'ai',
					text: "Failed to get response from API",
					rating: 0, // 初始评分为0
					feedback: "", // 初始反馈为空
					showFeedback: false, // 显示反馈部分
					callApiState:'failed'
				}
			]);
		} finally {
			setIsLoading(false); // 结束加载
			setInputValue(""); // 清空输入框
		}
	};

	// 处理评分更新
	const handleRatingChange = (index, rating) => {
		setIsEditingFeedback(true); // 标记正在编辑评价
		setConversation(prev => {
			const newConversation = [...prev];
			newConversation[index].rating = rating;
			return newConversation;
		});
	};

	// 处理反馈更新
	const handleFeedbackChange = (index, feedback) => {
		setIsEditingFeedback(true); // 标记正在编辑评价
		setConversation(prev => {
			const newConversation = [...prev];
			newConversation[index].feedback = feedback;
			return newConversation;
		});
	};

	// 处理反馈提交
	const handleFeedbackSubmit = async (index) => {
		const feedbackData = {
			index: index, // 反馈的索引
			score: conversation[index].rating, // 评分
			feedback: conversation[index].feedback // 反馈内容
		};

		try {
			// 调用反馈 API
			const response = await fetch('http://192.168.25.10:32250/generate_pg/feedback', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify(feedbackData)
			});

			if (!response.ok) {
				throw new Error('Feedback submission failed');
			}

			const result = await response.json();
			console.log('Feedback submitted successfully:', result);

			// 更新 UI
			setConversation(prev => {
				const newConversation = [...prev];
				newConversation[index].showFeedback = false; // 隐藏反馈部分
				return newConversation;
			});
			setIsEditingFeedback(false); // 重置编辑状态
			scrollToBottom(); // 提交反馈后滚动到底部
		} catch (error) {
			console.error('Error submitting feedback:', error);
			alert('提交反馈失败，请重试！');
		}
	};

	// 重新打开反馈部分
	const reopenFeedback = (index) => {
		setIsEditingFeedback(true); // 标记正在编辑评价
		setConversation(prev => {
			const newConversation = [...prev];
			newConversation[index].showFeedback = true; // 显示反馈部分
			return newConversation;
		});
	};

	// 清空聊天历史
	const clearChat = async () => {
		setConversation([]); // 清空对话历史
		try {
			const result=await fetch('http://192.168.25.10:32250/clear_history', {
				method: "POST",
			});
		} catch (error) {
			console.error("清空历史失败:", error);
		}
	};

	return (
		<div style={{ 
		display: 'flex', 
		flexDirection: 'column', 
		height: '100vh', // 设置高度为视口高度
		fontFamily: 'Arial, sans-serif',
		overflow: 'hidden', // 禁止整个界面滚动
		position: 'fixed', // 固定在屏幕上
		top: 0,
		left: 0,
		right: 0,
		bottom: 0,
		backgroundColor: '#fff' // 设置背景色
		}}>
		{/* 标题 */}
<h1 style={{ 
					 padding: '20px', 
					 backgroundColor: '#fff', 
					 borderBottom: '1px solid #ddd', 
					 margin: 0,
					 fontSize: '24px', // 调整字体大小
					 fontWeight: 'bold', // 调整字体粗细
					 color: '#333' // 调整字体颜色
					}}>
						生物医用材料聊天助手
							</h1>

{/* 聊天区域 */}
<div style={{ 
						flex: 1, 
						overflowY: 'auto', // 允许聊天区域滚动
						padding: '20px',
						backgroundColor: '#f9f9f9' // 设置聊天区域背景色
					 }}>
						 {conversation.map((msg, index) => (
							 <div key={index} style={{ 
																			 display: 'flex', 
																			 justifyContent: msg.type === 'user' ? 'flex-end' : 'flex-start', 
																			 marginBottom: '20px', // 调整消息之间的间距
																			 alignItems: 'flex-start' // 图标与消息顶部对齐
																			}}>
																				{/* AI 消息 */}
{msg.type === 'ai' && (
	<div style={{ 
	display: 'flex', 
	marginRight: '10px' 
	}}>
	<span role="img" aria-label="AI Icon" style={{ fontSize: '24px' }}>🤖</span> {/* AI Icon */}
</div>
)}
	<div style={{ 
							maxWidth: '60%', 
							padding: '12px 16px', // 调整内边距
							borderRadius: '10px', 
							backgroundColor: msg.type === 'user' ? '#007bff' : '#f1f1f1', 
							color: msg.type === 'user' ? '#fff' : '#333', // 调整字体颜色
							fontSize: '16px', // 调整字体大小
							lineHeight: '1.5', // 调整行高
							fontWeight: msg.type === 'user' ? '500' : '400', // 调整字体粗细
							wordWrap: 'break-word', // 允许长单词换行
							whiteSpace: 'pre-wrap', // 保留换行符
						 }}>
							 {msg.text}

{/* 显示反馈部分 */}
{msg.type === 'ai'&&msg.callApiState==='success'&& msg.showFeedback && (
	<div style={{ marginTop: '10px' }}>
	<div style={{ marginBottom: '10px' }}>
		<label>评分: </label>
{[1, 2, 3, 4, 5].map((star) => (
	<span
	key={star}
										 style={{ cursor: 'pointer', color: msg.rating >= star ? '#ffc107' : '#e4e5e9', fontSize: '24px' }}
onClick={() => handleRatingChange(index, star)}
	>
		★
</span>
))}
	</div>
<div style={{ marginBottom: '10px' }}>
	<textarea
value={msg.feedback}
onChange={(e) => handleFeedbackChange(index, e.target.value)}
placeholder="请输入您的评价..."
style={{ 
			 width: '100%', 
			 padding: '8px', 
			 borderRadius: '4px', 
			 border: '1px solid #ddd', 
			 outline: 'none', 
			 fontSize: '14px', 
			 lineHeight: '1.5' 
			}}
			/>
</div>
<button
onClick={() => handleFeedbackSubmit(index)}
style={{ 
			 padding: '8px 16px', 
			 backgroundColor: '#007bff', 
			 color: '#fff', 
			 border: 'none', 
			 borderRadius: '4px', 
			 cursor: 'pointer', 
			 fontSize: '14px' 
			}}
				>
					提交反馈
</button>
</div>
)}
{/* 重新打开反馈的按钮 */}
{msg.type === 'ai'&&msg.callApiState==='success' && !msg.showFeedback && (
	<div style={{ marginTop: '10px' }}>
	<button
onClick={() => reopenFeedback(index)}
style={{ 
			 padding: '8px 16px', 
			 backgroundColor: '#28a745', 
			 color: '#fff', 
			 border: 'none', 
			 borderRadius: '4px', 
			 cursor: 'pointer', 
			 fontSize: '14px' 
			}}
				>
					修改评价
</button>
</div>
)}
	</div>
</div>
))}
{/* 加载动画 */}
{isLoading && (
	<div style={{ 
	display: 'flex', 
	justifyContent: 'flex-start', 
	marginBottom: '20px', // 调整消息之间的间距
	alignItems: 'flex-start' // 图标与消息顶部对齐
	}}>
	<div style={{ 
							display: 'flex', 
							marginRight: '10px' 
						 }}>
							 <span role="img" aria-label="Loading Icon" style={{ fontSize: '24px' }}>⏳</span> {/* Loading Icon */}
</div>
<div style={{ 
						maxWidth: '60%', 
						padding: '12px 16px', // 调整内边距
						borderRadius: '10px', 
						backgroundColor: '#f1f1f1', 
						color: '#333', // 调整字体颜色
						fontSize: '16px', // 调整字体大小
						lineHeight: '1.5', // 调整行高
						fontWeight: '400' // 调整字体粗细
					 }}>
						 思考中...
							 </div>
</div>
)}
	<div ref={chatEndRef} /> {/* 用于指向聊天区域底部的空元素 */}
</div>

{/* 输入框区域：使用多行 textarea，并在底部内嵌发送和清除按钮 */}
<div style={{ 
						position: 'relative', 
						padding: '10px', 
						backgroundColor: '#fff', 
						borderTop: '1px solid #ddd'
					 }}>
						 <textarea
value={inputValue}
onChange={handleInputChange}
placeholder="输入你的问题..."
style={{ 
			 width: '95%',
			 minHeight: '60px', // 设置最小高度，可根据需要调整
			 padding: '12px 16px',
			 borderRadius: '4px',
			 border: '1px solid #ddd',
			 outline: 'none',
			 fontSize: '15px',
			 fontWeight: '400',
			 fontFamily: 'Arial, sans-serif',// 这里设置了新的字体
			 resize: 'vertical' // 允许垂直拉伸
			}}
			/>
<div style={{ 
						position: 'absolute', 
						bottom: '20px', 
						right: '25px', 
						display: 'flex', 
						gap: '5px'
					 }}>
						 <button
style={{ 
			 padding: '8px 16px', 
			 backgroundColor: '#fffff', 
			 border: 'none', 
			 borderRadius: '4px', 
			 cursor: 'pointer', 
			 fontSize: '14px', 
			 display: 'flex', 
			 alignItems: 'center', 
			 gap: '5px' 
			}}
				>
					<svg
width="16"
height="16"
viewBox="0 0 24 24"
fill="none"
stroke="currentColor"
strokeWidth="2"
strokeLinecap="round"
strokeLinejoin="round"
>
	<path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48" />
		</svg>
</button>
<button
onClick={callApi}
disabled={isLoading}
style={{ 
			 padding: '8px 12px',
			 backgroundColor: isLoading ? '#ccc' : '#007bff',
			 color: '#fff',
			 border: 'none',
			 borderRadius: '4px',
			 cursor: 'pointer',
			 fontSize: '12px',
			 fontWeight: '500',
			 display: 'flex',
			 alignItems: 'center',
			 gap: '5px'
			}}
				>
					<span role="img" aria-label="send icon">📤</span>
{isLoading ? '发送中...' : '发送'}
</button>
<button
onClick={clearChat}
style={{ 

			 padding: '10px 12px',
			 backgroundColor: '#dc3545',
			 color: '#fff',
			 border: 'none',
			 borderRadius: '4px',
			 cursor: 'pointer',
			 fontSize: '12px',
			 fontWeight: '500',
			 display: 'flex',
			 alignItems: 'center',

			 gap: '5px'
			}}
				>
					<span role="img" aria-label="clear icon">🗑️</span>
清除
	</button>
</div>
</div>
</div>
);
}

appsmith.onReady(() => {
	reactDom.render(<CustomWidget />, document.getElementById('root'));
});
