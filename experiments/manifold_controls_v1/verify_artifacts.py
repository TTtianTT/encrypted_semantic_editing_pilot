from mutil import *
import hashlib,py_compile,re
def main():
 verify();manifest=read(ROOT/'manifest.json')
 for name,digest in manifest.items():assert sha(ROOT/name)==digest,name
 for name,meta in read(ROOT/'results/evidence.json').items():
  assert sha(ROOT/name)==meta['sha256'];digest=hashlib.sha256();count=0
  with gzip.open(ROOT/name,'rb') as fo:
   for line in fo:digest.update(line);count+=1
  assert digest.hexdigest()==meta['uncompressed_sha256'] and count==meta['records'],name
 for path in ROOT.glob('*.py'):py_compile.compile(str(path),doraise=True)
 paper=ROOT.parents[1]/'paper';text=(paper/'main.tex').read_text();assert all((paper/name).exists() for name in re.findall(r'\\input\{([^}]+)\}',text));assert 'Numerical results will be' not in (paper/'followup_results.tex').read_text()
 assert read(ROOT/'global_gpu_audit.json')['global_peak_gpus']<=2
 dump('artifact_checks.json',dict(job_id=os.environ['SLURM_JOB_ID'],gpus=0,all_manifest_entries_verified=len(manifest),archives_decompress_and_match=True,all_scripts_compile=True,manuscript_inputs_exist=True,manuscript_sha256={name:sha(paper/name) for name in ['main.tex','followup_results.tex','README.txt']},tex_compiled=False,global_gpu_cap_verified=True))
 # This receipt is the only new artifact; refresh the manifest accordingly.
 manifest['artifact_checks.json']=sha(ROOT/'artifact_checks.json')
 report=ROOT/'REPORT.md';report.write_text(report.read_text()+f"\n末端核验已通过：Slurm作业{os.environ['SLURM_JOB_ID']}（0GPU）检查完整manifest、gzip解压后SHA、脚本语法及论文引用文件，见[artifact_checks.json](artifact_checks.json)。运行表是报告生成时的状态快照，末端核验可能仍显示PENDING；此完成收据为后续状态。\n")
 manifest['REPORT.md']=sha(report);dump('manifest.json',manifest);print('artifact verification passed',len(manifest),flush=True)
if __name__=='__main__':main()
