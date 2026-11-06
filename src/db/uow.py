
"""
UnitOfWork

It is a pattern to control transactions and manage the persistence of objects in a single unit of work. 
This module provides an implementation of the UnitOfWork pattern for database operations.

UnitOfWork = ACID

A - Atomic
C - Consistency
I - isolation
D - 


- atomic transacation

"""

from sqlalchemy.ext.asyncio import AsyncSession

class UnitOfWork:

    def __init__(self, session: AsyncSession):
        self.session = session


    async def __aenter__(self) -> "UnitOfWork":
        return self

    async def __aexit__(self, exc_type: type, exc_val: Exception, exc_tb: object) -> None:
        """
        exc_type: Type of the exception that occurred (if any)
        exc_val: Value of the exception that occurred (if any)
        exc_tb: Traceback object associated with the exception (if any)
        """

        try:
            if exc_type is None:
                await self.session.commit()
            else:
                await self.session.rollback()
        finally:
            await self.session.close()


def get_unit_of_work(session: AsyncSession) -> UnitOfWork:
    return UnitOfWork(session)

