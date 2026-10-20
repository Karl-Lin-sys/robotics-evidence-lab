# Primary sources and provenance

Checked 20 October 2026. The research comparison is a bounded shortlist, not an
exhaustive systematic review. Links below support only the associated claims.

## P1

Depth Anything: Unleashing the Power of Large-Scale Unlabeled Data, CVPR 2024.
[Proceedings](https://openaccess.thecvf.com/content/CVPR2024/html/Yang_Depth_Anything_Unleashing_the_Power_of_Large-Scale_Unlabeled_Data_CVPR_2024_paper.html)
and [official code](https://github.com/LiheYoung/Depth-Anything).
Supports inclusion as a monocular-depth baseline.

## P2

Depth Anything V2, NeurIPS 2024.
[Proceedings](https://proceedings.neurips.cc/paper_files/paper/2024/hash/26cfdcd8fe6fd75cc53e92963a656c58-Abstract-Conference.html)
and [official code and model licences](https://github.com/DepthAnything/Depth-Anything-V2).
Supports the relative/metric distinction, model variants and author-reported
improvements. No local model reproduction is claimed.

## P3

SplaTAM: Splat, Track & Map 3D Gaussians for Dense RGB-D SLAM, CVPR 2024.
[Proceedings](https://openaccess.thecvf.com/content/CVPR2024/html/Keetha_SplaTAM_Splat_Track__Map_3D_Gaussians_for_Dense_RGB-D_CVPR_2024_paper.html)
and [official code](https://github.com/spla-tam/SplaTAM).

## P4

OK-Robot: What Really Matters in Integrating Open-Knowledge Models for Robotics,
RSS 2024. [Proceedings](https://www.roboticsproceedings.org/rss20/p091.html)
and [official code](https://github.com/ok-robot/ok-robot).
Supports systems integration as a distinct problem from single-model accuracy.

## P5

ASAP: Aligning Simulation and Real-World Physics for Learning Agile Humanoid
Whole-Body Skills, RSS 2025.
[Proceedings](https://roboticsproceedings.org/rss21/p066.html)
and [official code](https://github.com/LeCAR-Lab/ASAP).
Supports simulation/real dynamics mismatch and a residual-action research remedy.

## P6

SWAD: Domain Generalization by Seeking Flat Minima, NeurIPS 2021 (December).
[Proceedings](https://proceedings.neurips.cc/paper_files/paper/2021/hash/bcb41ccdc4363c6848a1d760f26c28a0-Abstract.html).
Within the five-year diagnostic window, outside the three-year technology window.
Supports overfit-aware model selection/domain-generalization discussion; it is
not an adopted technology, copied implementation, or proof of our split policy.

## P7

How Re-sampling Helps for Long-Tail Learning?, NeurIPS 2023.
[Proceedings](https://proceedings.neurips.cc/paper_files/paper/2023/hash/eeffa70bcbbd43f6bd067edebc6595e8-Abstract-Conference.html).
Supports the warning that re-sampling with irrelevant contexts can learn spurious
correlations. The supplied code reports bias-sensitive metrics; it does not
implement this paper's context augmentation method.

## Frameworks

- [PyTorch inference_mode](https://docs.pytorch.org/docs/2.14/generated/torch.autograd.grad_mode.inference_mode.html)
  and [Module.eval](https://docs.pytorch.org/docs/2.14/generated/torch.nn.Module.html).
  The official stable URLs redirected to 2.14 at retrieval.
- [TensorFlow tf.function](https://www.tensorflow.org/api_docs/python/tf/function)
  and [Keras Model](https://www.tensorflow.org/api_docs/python/tf/keras/Model).
  Official current API URLs were checked; the rendered reference labels itself
  v2.16.1. This is not a claim that 2.16.1 is the latest installable package.
- [OpenCV VideoCapture](https://docs.opencv.org/4.x/d8/dfe/classcv_1_1VideoCapture.html).
  The 4.x reference resolved to 4.13.0. Package versions used for testing are
  separately recorded; documentation channel and wheel version may differ.

All project Python is original integration/evaluation code informed by those API
contracts. BFS, validation, limit arithmetic, and metric formulae are transparent
engineering implementations, not algorithms attributed to a recent ML paper.
This distinction is necessary: the permitted ML frameworks do not specify an
entire robot's mechanical, electrical, or real-time control system.

## Official legal sources

- [Taiwan Copyright Act](https://law.moj.gov.tw/ENG/LawClass/LawAll.aspx?pcode=J0070017),
  particularly reproduction and public transmission rights.
- [Taiwan Personal Data Protection Act](https://law.moj.gov.tw/ENG/LawClass/LawAll.aspx?pcode=I0050021).
- [Chinese Copyright Act](https://law.moj.gov.tw/LawClass/LawAll.aspx?PCode=J0070017)
  and [Chinese PDPA](https://law.moj.gov.tw/LawClass/LawAll.aspx?PCode=I0050021).

Use the applicable effective provisions and authoritative Chinese text for a
specific legal decision; online amendments and English translations may differ.
