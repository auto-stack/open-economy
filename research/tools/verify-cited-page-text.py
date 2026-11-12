"""Apply explicit, image-checked transcription corrections to local OCR.

This is a reproducible transcription recipe, not an automated fidelity check.
Every recorded correction was selected against the saved page image. Raw OCR
and original PDFs remain separate and unchanged. No new pages are read here.
"""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'wiki/derived/cited-page-text-2026-11-12'
LOG = []

def correct(work, page, text, old, new, kind='ocr_correction'):
    count = text.count(old)
    if count != 1:
        raise ValueError((work,page,old,count))
    LOG.append(dict(work_id=work,pdf_page=page,kind=kind,before=old,after=new))
    return text.replace(old,new)

def process(work, page, text):
    def c(old,new,kind='ocr_correction'):
        nonlocal text
        text=correct(work,page,text,old,new,kind)
    # Restore line-break hyphenation, retaining genuine compound hyphens.
    compounds={'capital-constrained','employer-employee','first-period',
               'information-intensive','one-person','short-or'}
    def join(m):
        pair=m.group(0)
        both=pair.replace(' ','')
        result=pair if both=='short-or' else both if both in compounds else both.replace('-','')
        if result!=pair:
            LOG.append(dict(work_id=work,pdf_page=page,kind='line_wrap_normalization',before=pair,after=result))
        return result
    text=re.sub(r'[A-Za-z]+- [a-z]+',join,text)
    if work=='L185' and page==2:
        c('THE BARGAINING PROBLEMI','THE BARGAINING PROBLEM [1]')
        c('Economic Behavior2','Economic Behavior [2]')
        c('The author wishes','[1] The author wishes')
        c('2 John von Neumann','[2] John von Neumann')
    elif work=='L185' and page==4:
        c('THE!BARGAINING PROBLEM 157 ','')
        c('(b) If 0 p 1 then u[pA + (1 — p) B] = pu(A) + (1 — p) u(B).',
          '(b) If $0 \\le p \\le 1$ then\n\n$$u[pA+(1-p)B]=p\\,u(A)+(1-p)\\,u(B).$$\n')
        c('[A, B] is a two-person anticipation and 0 p 1, then will be defined as Clearly',
          '[A, B] is a two-person anticipation and $0 \\le p \\le 1$, then\n\n'
          '$$p[A,B]+(1-p)[C,D]$$\n\nwill be defined as\n\n'
          '$$[pA+(1-p)C,\\ pB+(1-p)D].$$\n\nClearly', 'omitted_formula_restored')
    elif work=='L185' and page==5:
        c('158 JOH1•.i F. NASH, JR. ','')
    elif work=='L185' and page==6:
        # Windows OCR drops most subscripts/products in this page; replace the
        # affected passages explicitly rather than pretending its math is usable.
        c('THE BARGAINING PROBLEM 159 ','')
        c('Let and be utility functions','Let $u_1$ and $u_2$ be utility functions')
        c('6. If a is a point in S such that there exists another point ß in S with the property til(ß) > ul(a) and u2(ß) > u2(a), then a # c(S).',
          '6. If $\\alpha$ is a point in $S$ such that there exists another point $\\beta$ in $S$ with the property '
          '$u_1(\\beta)>u_1(\\alpha)$ and $u_2(\\beta)>u_2(\\alpha)$, then $\\alpha\\ne c(S)$.')
        c('utility operators ul and such','utility operators $u_1$ and $u_2$ such')
        c('the line = •','the line $u_1=u_2$.')
        c('8. If S is symmetric and ur and display this, then c(S) is a point of the form (a, a), that is, a point on the line = .',
          '8. If $S$ is symmetric and $u_1$ and $u_2$ display this, then $c(S)$ is a point of the form $(a,a)$, '
          'that is, a point on the line $u_1=u_2$.')
        c('first quadrant where ul is maximized','first quadrant where $u_1u_2$ is maximized')
        c('maximum ur .','maximum $u_1u_2$.')
        c('will + > 2,','will $u_1+u_2>2$,')
        c('with -k > 2','with $u_1+u_2>2$')
        c('a value of ur greater','a value of $u_1u_2$ greater')
        c('the region + 2','the region $u_1+u_2\\le 2$')
        c('the line ut = ,','the line $u_1=u_2$,')
        c('the line + QL2 = 2,','the line $u_1+u_2=2$,')
    elif work=='L189' and page==2:
        c('economcs','economics')
        c('legnsla tion. I','legislation.[1]')
        c('char• acterized','characterized')
        c('Henry Landau.','Henry Landau,')
        c('spring 1937 meetings','spring 1977 meetings')
        c('I Indeed,','[1] Indeed,')
        c('ratiomng','rationing')
        c('wouldl','would,')
        c('either: l)','either: 1)')
        c('re• payment','repayment')
        c('loan applications,','loan applications.')
        c("bank's profits,", "bank's profits.")
        # Footnotes are below the left column, not in the argument spanning columns.
        start=text.index('*Bell Telephone')
        end=text.index('they receive on the loan',start)
        notes=text[start:end]
        text=text[:start]+text[end:]
        text+='\n\n### Footnotes (printed page 393)\n\n'+notes
        LOG.append(dict(work_id=work,pdf_page=page,kind='column_order',
                        before='Left-column footnotes interrupt the last left-column sentence',
                        after='Left body, right body, then left-column footnotes'))
    elif work=='L189' and page==3:
        c("THE AMERICAN ECONOMIC REVIEW JUNE '98! INTEREST RATE FIGURE . THERE Extsrs AN INTEREST RATE wr--nct-t MAMMIz.Es EXPECTED RETURN TO THE BANK ",
          '### Figure 1 — checked transcription\n\n'
          'There Exists an Interest Rate which Maximizes the Expected Return to the Bank.\n\n'
          'Vertical axis: EXPECTED RETURN TO THE BANK. Horizontal axis: INTEREST RATE. '
          'The indicated maximum is at $\\hat r^{*}$. '
          '[转录说明：曲线为示意图，未读取数值或添加估计数据。]\n\n### Article body\n\n')
        c('retum to the loan','return to the loan')
        c('as the "bank-optimat" rate,','as the "bank-optimal" rate, $\\hat r^{*}$.')
        c('return at F*','return at $\\hat r^{*}$')
        c('that at i*','that at $\\hat r^{*}$')
        c('demand at it is','demand at $\\hat r^{*}$, it is')
        c('more than F*.','more than $\\hat r^{*}$.')
        c('at interest rate and','at interest rate $\\hat r^{*}$, and')
        c('above F*','above $\\hat r^{*}$')
        c('deterrmned','determined')
        c('borrowers, In','borrowers. In')
        c('indis• 2 tinguishable from those who receive loans.',
          'indistinguishable from those who receive loans.[2]')
        c('conceming','concerning')
        c('different Size','different size')
        c("IAfter this paper", "[2] After this paper")
    elif work=='L189' and page==4:
        c('VOL 71 NO. 3 STIGLITZ AND WEISS: CREDIT RATIONING 395 ','')
        c('groups Of individuals','groups of individuals')
        c('they would. 3','they would.[3]')
        c("a ' 'price-taking\" equilibrium",'a "price-taking" equilibrium')
        c('equilibrium interest rates, If,','equilibrium interest rates. If,')
        c('L Interest Rate as a Screening Device','I. Interest Rate as a Screening Device')
        start=text.index('3 n•eere is another')
        end=text.index('of projects; for each', start)
        notes=text[start:end]
        text=text[:start]+text[end:]
        text+='\n\n### Footnote 3 (left column)\n\n'+notes
        c('3 n•eere is another','[3] There is another')
        c('refuse to Ieod','refuse to lend')
        c('for each project 8','for each project $\\theta$')
        c('same mean retum.','same mean return.')
        c('returns4 as F(R, 0) and the density function as f(R, 8), and we assume that greater 0 corresponds to greater risk in the sense of mean preserving spreads: (see Rothschild-Stiglitz), i.e., for 9, >02, if then for y',
          'returns[4] as $F(R,\\theta)$ and the density function as $f(R,\\theta)$, '
          'and we assume that greater $\\theta$ corresponds to greater risk in the sense of mean preserving spreads[5] '
          '(see Rothschild-Stiglitz), i.e., for $\\theta_1>\\theta_2$, if\n\n'
          '$$\\tag{1} \\int_0^\\infty Rf(R,\\theta_1)\\,dR=\\int_0^\\infty Rf(R,\\theta_2)\\,dR$$\n\n'
          'then for $y\\ge 0$,\n\n'
          '$$\\tag{2} \\int_0^y F(R,\\theta_1)\\,dR\\ge\\int_0^y F(R,\\theta_2)\\,dR.$$\n',
          'omitted_formula_restored')
        c('the interst rate is i,','the interst rate is $\\hat r$,')
        c('prornised amount,6','promised amount,[6]')
        c('i.e., if (3) 4 These', 'i.e., if\n\n$$\\tag{3} C+R\\le B(1+\\hat r).$$\n\n### Footnotes 4–6 (right column)\n\n[4] These',
          'omitted_formula_restored')
        c('firm, 5 Michael','firm.\n\n[5] Michael')
        c('conditions (I) and (2)','conditions (1) and (2)')
        c('project l,','project 1,')
        c('prefers project t to project 2. 6 This','prefers project 1 to project 2.\n\n[6] This')
        c('possible definition-','possible definition.')
        c('in default if + i).','in default if $R<B(1+\\hat r)$.','omitted_formula_restored')
        c('usually shalt ignore','usually shall ignore')
        c('Throughout thus section','Throughout this section')
        LOG.append(dict(work_id=work,pdf_page=page,kind='column_order',
                        before='Footnote 3 separates the two body columns',
                        after='Left and right body joined; right footnotes then separately labelled left footnote 3'))
    elif work=='L190' and page==2:
        c('vol. cxll','Vol. CXII')
        c('0 1997 by','© 1997 by')
    elif work=='L190' and page==3:
        c('664 QUARTERLY JOURNAL OF ECONOMICS ','')
        c('price.l Yet','price.[1] Yet')
        c('lending.2','lending.[2]')
        c('subsection 111B','subsection IIIB')
        c('time.3','time.[3]')
        c('I. Vihriala','[1] Vihriala')
        c('2. For an extensive','[2] For an extensive')
        c('3. Vihriala','[3] Vihriala')
    elif work=='L190' and page==4:
        c('FINANCIAL INTERMEDIATION AND LOANABLE FUNDS 665 ','')
        c('intensively.4','intensively.[4]')
        c('4. Since our model','[4] Since our model')
        c('subsection 111.3','subsection III.3')
    elif work=='L190' and page==5:
        c('666 QUARTERLY JOURNAL OF ECONOMICS ','')
        c('collateral. implication of our model','collateral. Another implication of our model','omitted_words_restored')
        c('pos- Sible','possible')
        c('insights.5','insights.[5]')
        c('intermediaries.6','intermediaries.[6]')
        c('5. See Jaffee','[5] See Jaffee')
        c('6. In independent','[6] In independent')
    elif work=='L190' and page==6:
        c('667 FINANCIAL INTERMEDIATION AND LOANABLE FUNDS ','')
        c('THE BASIc MODEL','THE BASIC MODEL')
        c('11.1. The Real Sector','II.1. The Real Sector')
        c('value A.7','value A.[7]')
        c('K f = JAdG(A).','$K_f=\\int A\\,dG(A)$.')
        c('I > O','I > 0')
        c('Ap = —PL > 0.','\n\n$$\\Delta p=p_H-p_L>0.$$\n','omitted_formula_restored')
        c('7. To the extent','[7] To the extent')
    elif work=='L190' and page==7:
        c('668 Project QUARTERLY JOURNAL OF ECONOMICS Good Bad (Iow private benefit) Bad (high private bex•efit) Private berrefit Probabilit Y of success FIGURE I ',
          '### Figure I — checked table transcription\n\n'
          '| Project | Good | Bad (low private benefit) | Bad (high private benefit) |\n'
          '|---|---|---|---|\n| Private benefit | 0 | b | B |\n'
          '| Probability of success | $p_H$ | $p_L$ | $p_L$ |\n\n### Article body\n\n',
          'figure_table_restored')
        c('denoted by my,','denoted by $\\gamma$,')
        c('that is, (1) O > PLR -YI + B.',
          'that is,\n\n$$\\tag{1} p_HR-\\gamma I>0>p_LR-\\gamma I+B.$$\n',
          'omitted_formula_restored')
        c('11.2. The Financial Sector','II.2. The Financial Sector')
        c('The financial secto+','The financial sector')
    # Remove repeated running page number where recognised; page mapping lives in heading.
    if work=='L185' and page==2:
        text=re.sub(r' 155\s*$','',text)
    if work=='L189' and page==2:
        text=text.replace(' could 393\n',' could\n')
    # Paragraph boundaries preserve source wording; headings/footnotes are transcription layout.
    anchors = {
        ('L185',2):['INTRODUCTION','A TWO-PERSON','The economic situations','This is the classical','In general terms,','[1] The author','[2] John'],
        ('L185',4):['(a) u(A)','(b) If','This is the important','TWO PERSON THEORY','In Theory of Games','It is our viewpoint','We may define','In a bargaining situation'],
        ('L185',5):['We may produce','It is necessary','We shall regard','Now since our solution'],
        ('L185',6):['6. If','7. If','We say that','8. If','The first assumption','We now show','We may now construct','We shall now give'],
        ('L189',2):['Why is credit rationed?','One method','The object of this paper','The adverse selection aspect','Similarly,','In a world with perfect','[1] Indeed,'],
        ('L189',3):['For both these reasons,','Both the demand','But the interest rate is not','Consequently,','It is not our argument','This paper thus provides','We reserve the term','[2] After'],
        ('L189',4):['In our construction','Although these results','I. Interest Rate','In this section','Different firms','If the individual borrows'],
        ('L190',2):['We study an incentive','I. INTRODUCTION','During the late','Scandinavia seems','* We are grateful','© 1997'],
        ('L190',3):['First, bank lending','The final,','The purpose','[1] Vihriala','[2] For','[3] Vihriala'],
        ('L190',4):['We are primarily','Our model features','[4] Since'],
        ('L190',5):['Another implication','Our model builds','The next section','[5] See','[6] In'],
        ('L190',6):['II. THE BASIC MODEL','The model has three','II.1. The Real Sector','There is a continuum','In the basic version','Firms are run','We assume that','[7] To'],
        ('L190',7):['We introduce two','II.2. The Financial Sector','The financial sector'],
    }
    for anchor in anchors.get((work,page),[]):
        text=text.replace(' '+anchor,'\n\n'+anchor)
    return text.strip()

def main():
    manifest=json.loads((OUT/'provenance.json').read_text(encoding='utf-8'))
    for source in manifest['sources']:
        work=source['work_id']
        title={'L185':'Nash 1950 — The Bargaining Problem',
               'L189':'Stiglitz–Weiss 1981 — Credit Rationing',
               'L190':'Holmström–Tirole 1997 — Financial Intermediation'}[work]
        parts=[f'# {title}：已引用页文字\n\n'
               '2026-11-12。本地Windows英文OCR后对照逐页图像修订；不是出版方文字版，也不是整篇OCR。'
               '行末断词、页眉和脚注排版已规范化；公式以LaTeX转录，插入说明使用中文方括号。'
               '原始识别结果及逐项更正分别保留。来源原件、元数据和旧基线不改动。\n']
        for item in source['page_scope']:
            page=item['pdf_page']; printed=item['printed_page']
            raw=(OUT/item['raw_text']).read_text(encoding='utf-8').strip()
            body=process(work,page,raw)
            heading=f'## 印刷页 {printed} · PDF文件第 {page} 页'
            links=f'[扫描图像]({Path(item["image"]).name}) · [原始OCR]({Path(item["raw_text"]).name})'
            note=''
            if work=='L185' and page==4:
                note='\n\n[范围说明：本页开头承接未纳入的156页；结尾继续至已纳入的158页。]\n'
            if work=='L189' and page==4:
                note=('\n\n[校核说明：原件正文写 $\\theta_1>\\theta_2$，式(2)为 $\\ge$；'
                      '脚注5却称project 2比project 1方差更大。正文与脚注存在编号方向不一致的疑点，'
                      '本转录保留两处原样，未擅自改正，也未核对出版方勘误。'
                      '脚注6的最后一句在下一页继续，本选页未补全。原文“interst”按扫描保留。]\n')
            if work=='L190' and page==2:
                note='\n\n[页码说明：本页版心未印阿拉伯页码；663依据原件封面页段663–691及下一页可见664对应。]\n'
            if work=='L190' and page==7:
                note='\n\n[范围说明：最后一句在669页继续；未纳入669页，不补写后续监督约束或均衡公式。]\n'
            text=heading+'\n\n'+links+'\n\n'+body+note
            target=OUT/work/f'pdf-{page:02d}-print-{printed}.verified.md'
            target.write_text(text+'\n',encoding='utf-8')
            item['verified_text']=target.relative_to(OUT).as_posix()
            item['visual_review']='page image and OCR compared; formula and printed-page mapping checked'
            item['printed_page_visible']=not(work=='L190' and page==2)
            parts.append(text)
        (OUT/work/'cited-pages.md').write_text('\n\n---\n\n'.join(parts)+'\n',encoding='utf-8')
        source['verified_text']=f'{work}/cited-pages.md'
    manifest['status']='cited_pages_ocr_and_visual_transcription_checked'
    manifest['review_limit']='Single-assistant visual transcription; not independent double entry, full-paper OCR, or external scientific validation.'
    manifest['source_text_issue']='L189 printed395: theta1>theta2 and equation(2)>= preserved; footnote5 project-number direction flagged, not emended.'
    (OUT/'provenance.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (OUT/'corrections.json').write_text(json.dumps(LOG,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Verified pages:',sum(len(s['page_scope']) for s in manifest['sources']))
    print('Recorded corrections/layout normalizations:',len(LOG))

if __name__=='__main__':
    main()
