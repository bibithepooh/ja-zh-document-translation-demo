const button=document.querySelector('#runDemo'),stages=[...document.querySelectorAll('.pipeline>div')],result=document.querySelector('#result'),type=document.querySelector('#fileType'),fileInput=document.querySelector('#demoFile'),dropzone=document.querySelector('#dropzone'),fileStatus=document.querySelector('#fileStatus');
const types={pdf:'PDF',doc:'DOCX',docx:'DOCX',ppt:'PPTX',pptx:'PPTX',xls:'XLSX',xlsx:'XLSX',txt:'TXT',md:'TXT',png:'IMAGE',jpg:'IMAGE',jpeg:'IMAGE',webp:'IMAGE'};
function useFile(file){if(!file)return;const ext=file.name.split('.').pop().toLowerCase();type.value=types[ext]||'TXT';fileStatus.textContent=`已选择：${file.name}（${(file.size/1024).toFixed(1)} KB）`}
fileInput.addEventListener('change',()=>useFile(fileInput.files[0]));
['dragenter','dragover'].forEach(event=>dropzone.addEventListener(event,e=>{e.preventDefault();dropzone.classList.add('dragging')}));
['dragleave','drop'].forEach(event=>dropzone.addEventListener(event,e=>{e.preventDefault();dropzone.classList.remove('dragging')}));
dropzone.addEventListener('drop',e=>useFile(e.dataTransfer.files[0]));
button.addEventListener('click',async()=>{
  const file=fileInput.files[0];
  if(!file){result.innerHTML='<div class="empty"><strong>!</strong><p>请先选择一份 PDF 文件</p></div>';return}
  button.disabled=true;button.textContent='正在本地翻译…';stages.forEach(s=>s.classList.remove('active'));
  result.innerHTML='<div class="empty"><strong>…</strong><p>首次运行会加载离线模型，整份文档可能需要几分钟</p></div>';
  const form=new FormData();form.append('file',file);
  try{
    stages.slice(0,3).forEach(s=>s.classList.add('active'));
    const response=await fetch('/api/translate',{method:'POST',body:form});
    const data=await response.json();
    if(!response.ok)throw new Error(data.error||'处理失败');
    stages.forEach(s=>s.classList.add('active'));
    result.innerHTML=`<div class="result-block"><h4>处理完成</h4><p>${data.engine}<br>共处理 ${data.sheets.length} 个工作表、${data.text_count} 个日语单元格。</p></div><div class="result-block"><h4>下载结果</h4><p><a class="button primary" href="${data.bilingual_url}">下载翻译版</a> <a class="button secondary" href="${data.translated_url}">下载纯中文版</a></p></div><div class="checks"><div class="check"><b>✓</b>日语原文完整保留在前</div><div class="check"><b>✓</b>中文译文另起一行，以蓝色小字附在后</div><div class="check"><b>✓</b>保留单元格格式、合并关系和下拉框</div><div class="check"><b>→</b>在线模式仅用于公开样例，正式交付前仍需人工复核</div></div>`;
  }catch(error){result.innerHTML=`<div class="empty"><strong>!</strong><p>${error.message}</p></div>`}
  finally{button.disabled=false;button.textContent='翻译并生成 Excel'}
});
