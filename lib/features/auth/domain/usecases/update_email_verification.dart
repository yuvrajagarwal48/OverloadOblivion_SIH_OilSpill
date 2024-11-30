
import 'package:fpdart/fpdart.dart';
import 'package:spill_sentinel/core/error/failure.dart';
import 'package:spill_sentinel/core/usecase/usecase.dart';
import 'package:spill_sentinel/features/auth/domain/repository/auth_repository.dart';


class UpdateEmailVerification implements Usecase<void, NoParams> {
  final AuthRepository repository;
  UpdateEmailVerification(this.repository);
  @override
  Future<Either<Failure,void>> call(NoParams params) {
    return repository.updateEmailVerification();
  }
}


