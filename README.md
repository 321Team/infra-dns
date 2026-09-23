# infra-dns
Phase 1 BIND Primary/Secondary DNS source: zones, query/transfer ACLs, validation and recovery runbooks; Phase 2 hybrid DNS only after D23. No TSIG keys or secrets.

## 변경 절차

리뷰·병합과 Lead 판단은 [리뷰 정책](docs/REVIEW_POLICY.md)을 따릅니다. 코드·실행 설정·혼합 PR은 독립 리뷰, 문서만 변경한 PR은 책임 Lead가 판단합니다. 사전 검증(Pre-check) 코드는 담당 Lead 권한으로 바로 병합할 수 있습니다. 운영 DNS 서버에 적용하기 전에는 해당 SHA의 코드 리뷰가 필수입니다.
