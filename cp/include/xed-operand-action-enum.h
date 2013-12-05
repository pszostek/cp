/*BEGIN_LEGAL 
Intel Open Source License 

Copyright (c) 2002-2013 Intel Corporation. All rights reserved.
 
Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

Redistributions of source code must retain the above copyright notice,
this list of conditions and the following disclaimer. Redistributions
in binary form must reproduce the above copyright notice, this list of
conditions and the following disclaimer in the documentation and/or
other materials provided with the distribution. Neither the name of
the Intel Corporation nor the names of its contributors may be used to
endorse or promote products derived from this software without
specific prior written permission.
 
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
``AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE INTEL OR
ITS CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
END_LEGAL */
/// @file xed-operand-action-enum.h

// This file was automatically generated.
// Do not edit this file.

#if !defined(_XED_OPERAND_ACTION_ENUM_H_)
# define _XED_OPERAND_ACTION_ENUM_H_
#include "xed-common-hdrs.h"
typedef enum {
 XED_OPERAND_ACTION_INVALID,
 XED_OPERAND_ACTION_RW, ///< Read and written (must write)
 XED_OPERAND_ACTION_R, ///< Read-only
 XED_OPERAND_ACTION_W, ///< Write-only (must write)
 XED_OPERAND_ACTION_RCW, ///< Read and conditionlly written (may write)
 XED_OPERAND_ACTION_CW, ///< Conditionlly written (may write)
 XED_OPERAND_ACTION_CRW, ///< Conditionlly read, always written (must write)
 XED_OPERAND_ACTION_CR, ///< Conditional read
 XED_OPERAND_ACTION_LAST
} xed_operand_action_enum_t;

/// This converts strings to #xed_operand_action_enum_t types.
/// @param s A C-string.
/// @return #xed_operand_action_enum_t
/// @ingroup ENUM
XED_DLL_EXPORT xed_operand_action_enum_t str2xed_operand_action_enum_t(const char* s);
/// This converts strings to #xed_operand_action_enum_t types.
/// @param p An enumeration element of type xed_operand_action_enum_t.
/// @return string
/// @ingroup ENUM
XED_DLL_EXPORT const char* xed_operand_action_enum_t2str(const xed_operand_action_enum_t p);

/// Returns the last element of the enumeration
/// @return xed_operand_action_enum_t The last element of the enumeration.
/// @ingroup ENUM
XED_DLL_EXPORT xed_operand_action_enum_t xed_operand_action_enum_t_last(void);
#endif
