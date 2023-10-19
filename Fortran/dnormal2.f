!=========================================================================
! Subroutine dnorm2
!=========================================================================
      SUBROUTINE dnormal2(vec, n, ind, dm, sd)
      Implicit None

      Integer :: n
      Integer :: ind
      Integer :: i

      Real*8 :: vec(n)      ! set of variables
      Real*8 :: dm          ! mean value
      Real*8 :: sd          ! standard deviation

      dm = 0.0
      do i = 1, n
        if(i.ne.ind) dm = dm + vec(i)
      enddo
      dm = dm / dble(n)

      sd = 0.0
      do i = 1, n
        if(i.ne.ind) sd = sd + (vec(i) - dm)**2.0
      enddo
      sd = dsqrt (sd / dble(n-1))    

               dm = 0.0
               sd = 1.0

      do i = 1, n
        if(i.ne.ind) vec(i) = (vec(i) - dm)/sd
      enddo

      END
